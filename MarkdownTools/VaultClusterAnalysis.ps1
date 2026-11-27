<#
.SYNOPSIS
    Finds conceptual clusters in an Obsidian vault of Markdown notes.

.DESCRIPTION
    Single-file, standalone analyzer. Reads notes only. Writes all output to -OutputDir
    (temp by default), so the vault is never modified.

    Signals used:
      - YAML tags (frontmatter, both list and inline forms)
      - Curated root keywords from Taxonomy\Keywords (Zettelkasten timestamp and
        trailing "Root" removed from each filename)
      - Root keywords matched in titles/tags only for "hard core" membership
      - Wikilink counts as a cohesion signal
      - Folder placement, workflow status, and year for readiness/momentum

    A note is "hard core" in a cluster when it has 2+ matching tags, or 1 matching
    tag plus 1 matching root keyword in title/tags, or 2+ matching roots.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\VaultClusterAnalysis.ps1 -VaultPath "C:\Users\hittj\Github\obsidian"

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\VaultClusterAnalysis.ps1 -VaultPath "D:\notes" -OutputDir "D:\analysis" -IncludeRawSignals -SinceYear 2025
#>
[CmdletBinding()]
param(
    [string]$VaultPath = (Get-Location).Path,
    [string]$OutputDir = (Join-Path $env:TEMP 'VaultClusterAnalysis'),
    [int]$SinceYear = 2024,
    [int]$TopN = 500,
    [switch]$IncludeRawSignals,
    [switch]$PassThru
)

$ErrorActionPreference = 'Stop'

# ============================================================================
# EDIT HERE: cluster definitions.
# anchors = root keyword names from Taxonomy\Keywords (case insensitive).
# tags    = YAML tag values, no leading hash.
# Add, remove, or rename clusters freely; the rest of the script is generic.
# ============================================================================
function Get-ClusterDefinitions {
    return [ordered]@{
        'Lead generation and direct response' = @{
            anchors = 'Lead Generation|Profitable Customer|Conversion Rate|Direct Mail|Direct Marketing|Customer Loyalty|Attract Customers|Demand Generation|Sales Offer|Customer Satisfaction|Customer Avatar|Appointment Setting';
            tags = 'lead-generation|direct-response|direct-marketing|conversion-rate|conversion-optimization|sales-letter|high-ticket|headline-testing|direct-mail|list-building|mailing-list'
        }
        'Content SEO and topical authority' = @{
            anchors = 'Content Marketing|Keyword Cluster|Technical SEO|Business Blogging|Content Syndication';
            tags = 'content-marketing|keyword-research|topical-mapping|search-optimization|article-marketing|content-development|search-engine|increase-traffic|website-traffic'
        }
        'Consulting practice and expert positioning' = @{
            anchors = 'Paid Consultation|Recognized Expert|Establish Credibility|Strategic Consulting|Executive Relations|Consultant Website|Publishing Services';
            tags = 'paid-consultation|recognized-expert|initial-consultation|discovery-call|business-development|strategic-relations|business-relationship|instant-credibility|coaching-program|mastermind-program|business-networking'
        }
        'Knowledge work and productivity' = @{
            anchors = 'Note Taking|Organize Information|Knowledge Management|Information Management|Project Management|Goal Setting|Schedule Advisory|Administrative Services';
            tags = 'note-taking|critical-thinking|problem-solving|more-done|peak-performance|increase-productivity|time-management|task-management|goal-setting|second-brain|knowledge-management|information-management|organize-information|project-management'
        }
        'Homestead permaculture and livestock' = @{
            anchors = 'Permaculture Design|Regenerative Agriculture|Land Management|Erosion Control|Raising Goats|Organic Gardening|Soil Health|Start Homestead|Homestead Management|Clearing Land|Brush Clearing|Bamboo Removal|Forest Mulcher|Pasture Management|Wildlife Habitat|Farm Manager|Farm Hand|Syntrophic Agroforestry|Custom Sawmilling';
            tags = 'raising-goats|permaculture-design|homesteading-skills|land-management|food-security|erosion-control|off-grid|making-compost|community-garden|organic-recycling|organic-waste|bamboo-removal|clearing-land|start-homesteading'
        }
        'Risk compliance and continuity' = @{
            anchors = 'Risk Management|Operational Risk|Asset Protection|Insider Threat';
            tags = 'risk-management|operational-risk|compliance-risk|disaster-recovery|money-laundering|business-continuity'
        }
        'Personal finance and wealth' = @{
            anchors = 'Cash Management|Debt Management|Wealth Management|Recession Proof|Passive Income|Asset Protection';
            tags = 'personal-finance|wealth-building|cash-flow|cash-management|debt-management|increase-wealth|net-worth|investment-strategy|balanced-portfolio|intentional-thrift|increase-income'
        }
        'Information products and monetization' = @{
            anchors = 'Membership Site|Publishing Services|Platform Sales|Wealth Newsletter';
            tags = 'membership-site|information-marketing|information-product|special-report|paid-newsletter|coaching-program|mastermind-program|prospect-newsletter'
        }
        'Governance liberty and contrarian politics' = @{
            anchors = 'Media Bias|Political Influence|Personal Liberty|Modern Slavery|Dark Money|Conspiracy Theory|Social Engineering';
            tags = 'government-control|social-engineering|mind-control|government-corruption|media-bias|conspiracy-theory|personal-liberty|dark-money|social-influence'
        }
        'Emergency preparedness and off grid' = @{
            anchors = 'Survival Skills|Clean Water|Pit Latrine|Off Grid';
            tags = '72-hour-grab-and-go|three-week-snowstorm|survival-skills|emergency-preparedness|clean-water|off-grid'
        }
        'Career development and job search' = @{
            anchors = 'Career Development';
            tags = 'job-search|career-development'
        }
        'AI assisted writing and research' = @{
            anchors = 'Entity Explorer|Data Integration';
            tags = 'artificial-intelligence|language-model|writing-tools|copilot-conversation|generative-ai'
        }
        'Public relations speaking and events' = @{
            anchors = '';
            tags = 'public-relations|press-release|public-speaking|event-marketing|event-promotion'
        }
        'Disaster and hurricane marketing' = @{
            anchors = '';
            tags = 'disaster-marketing|hurricane-marketing'
        }
    }
}
# ============================================================================

function Add-Count {
    param([hashtable]$Counter, [string]$Key)
    if ([string]::IsNullOrWhiteSpace($Key)) { return }
    if ($Counter.ContainsKey($Key)) { $Counter[$Key]++ } else { $Counter[$Key] = 1 }
}

function Get-CleanPath {
    param([string]$Path)
    $p = [IO.Path]::GetFullPath($Path)
    return $p.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
}

function Get-VaultAnchors {
    param([string]$Root)
    $dir = Join-Path $Root 'Taxonomy\Keywords'
    $names = @()
    if (Test-Path -LiteralPath $dir) {
        foreach ($f in [IO.Directory]::GetFiles($dir, '*.md')) {
            $n = [IO.Path]::GetFileNameWithoutExtension($f)
            $n = $n -replace '^\d{12}\s+', '' -replace '\s+Root\s*$', ''
            if ($n.Trim()) { $names += $n.Trim() }
        }
    } else {
        Write-Warning 'Taxonomy\Keywords not found. Root-keyword matching disabled; tags only.'
    }
    return @($names | Sort-Object -Unique)
}

function New-AnchorMatcher {
    param([string[]]$Names)
    $lookup = @{}
    foreach ($a in $Names) { $lookup[$a.ToLower()] = $a }
    $parts = @($Names | Sort-Object { $_.Length } -Descending | ForEach-Object { [regex]::Escape($_.ToLower()) })
    $pattern = if ($parts.Count -gt 0) { $parts -join '|' } else { '(?!)' }
    return @{ Lookup = $lookup; Pattern = $pattern }
}

function Get-NoisePattern {
    return '(?i)resume|invoice|itinerary|huddle|agent__|untitled chat|^\d{4}-\d{2}-\d{2}$|^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$|public information officer|eeoc|medical|reconcile|cover letter|job search items|week ending|editorial calendar|topics catalog|work in progress kanban'
}

function Write-RankedTable {
    param([hashtable]$Counter, [string]$Directory, [string]$File, [string]$NameA, [string]$NameB, [int]$Limit)
    $rows = @()
    foreach ($k in $Counter.Keys) { $rows += "$k`t$($Counter[$k])" }
    $rows = @($rows | Sort-Object { [int]($_ -split "`t")[-1] } -Descending | Select-Object -First $Limit)
    [IO.File]::WriteAllLines((Join-Path $Directory $File), (@("$NameA`t$NameB") + $rows))
}

function Write-JsonUtf8 {
    param($Object, [string]$Path)
    $json = $Object | ConvertTo-Json -Depth 4
    $enc = New-Object Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($Path, $json, $enc)
}

function Write-Tsv {
    param([string[]]$Lines, [string]$Path)
    [IO.File]::WriteAllLines($Path, $Lines)
}

function Invoke-Scan {
    param([string]$Root, [string]$Out, [int]$Limit, [switch]$Raw)

    $anchorNames = Get-VaultAnchors -Root $Root
    $matcher = New-AnchorMatcher -Names $anchorNames
    $outRoot = Get-CleanPath -Path $Out

    $tagFreq = @{}; $pairFreq = @{}; $anchorFreq = @{}; $linkFreq = @{}
    $typeFreq = @{}; $statusFreq = @{}; $platformFreq = @{}
    $folderFreq = @{}; $subFolderFreq = @{}; $titleBi = @{}; $titleTri = @{}
    $rows = New-Object System.Collections.Generic.List[string]
    $scanned = 0; $taggedNotes = 0; $tagAssignments = 0; $linkedNotes = 0

    $files = [IO.Directory]::EnumerateFiles($Root, '*.md', [IO.SearchOption]::AllDirectories)
    foreach ($full in $files) {
        if ($full -match '\\\.git\\|\\\.trash\\|\\\.obsidian|\\node_modules\\') { continue }
        if ($full.StartsWith($outRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { continue }

        try { $text = [IO.File]::ReadAllText($full) } catch { continue }
        $scanned++

        $rel = $full.Substring($Root.Length + 1)
        $parts = $rel -split '\\'
        $top = $parts[0]
        $sub = if ($parts.Count -gt 1) { $parts[1] } else { '' }
        Add-Count $folderFreq $top
        Add-Count $subFolderFreq "$top\$sub"

        $body = $text
        $tags = @()
        if ($text.StartsWith('---')) {
            $idx = $text.IndexOf("`n---", 3)
            if ($idx -gt 0) {
                $fm = $text.Substring(0, $idx)
                $body = $text.Substring($idx + 4)
                $inTags = $false
                foreach ($line in ($fm -split "`r?`n")) {
                    if ($line -match '^tags\s*:\s*(.*)$') {
                        $inTags = $true
                        $rest = $Matches[1].Trim()
                        if ($rest -match '^\[(.*)\]\s*$') {
                            foreach ($t in ($Matches[1] -split ',')) { $tags += ($t -replace '^[#\s]+|[\s\]]+$', '') }
                            $inTags = $false
                        } elseif ($rest -match '^\S') {
                            $tags += ($rest -replace '^[#\s]+|[\s\]]+$', '')
                        }
                    } elseif ($inTags) {
                        if ($line -match '^\s*-\s+(.+?)\s*$') { $tags += ($Matches[1] -replace '^[#\s]+', '') }
                        elseif ($line -match '^\S') { $inTags = $false }
                    }
                    if ($line -match '^type\s*:\s*(\S+)') { Add-Count $typeFreq $Matches[1].ToLower() }
                    if ($line -match '^status\s*:\s*(\S+)') { Add-Count $statusFreq $Matches[1].ToLower() }
                    if ($line -match '^platform\s*:\s*(\S+)') { Add-Count $platformFreq $Matches[1].ToLower() }
                }
            }
        }

        $tags = @($tags | Where-Object { $_ -and $_ -ne 'null' -and $_ -ne '[]' } |
                  ForEach-Object { $_.ToLower() } | Sort-Object -Unique)
        if ($tags.Count -gt 0) {
            $taggedNotes++; $tagAssignments += $tags.Count
            foreach ($t in $tags) { Add-Count $tagFreq $t }
            for ($i = 0; $i -lt $tags.Count; $i++) {
                for ($j = $i + 1; $j -lt $tags.Count; $j++) {
                    Add-Count $pairFreq "$($tags[$i])`t$($tags[$j])"
                }
            }
        }

        $links = ([regex]::Matches($text, '\[\[([^\]\|#]+)')).Count
        if ($links -gt 0) { $linkedNotes++ }
        foreach ($m in [regex]::Matches($text, '\[\[([^\]\|#]+)')) {
            $t = $m.Groups[1].Value.Trim()
            if ($t) { Add-Count $linkFreq $t }
        }

        $base = [IO.Path]::GetFileNameWithoutExtension($rel) -replace '^\d{12}\s+', ''
        $words = @($base.ToLower() -split '[^a-z0-9]+' | Where-Object { $_ -and $_.Length -gt 1 })
        for ($i = 0; $i -lt $words.Count - 1; $i++) {
            Add-Count $titleBi "$($words[$i]) $($words[$i+1])"
            if ($i -lt $words.Count - 2) { Add-Count $titleTri "$($words[$i]) $($words[$i+1]) $($words[$i+2])" }
        }

        $b = $body
        if ($b.Length -gt 9000) { $b = $b.Substring(0, 9000) }
        $b = [regex]::Replace($b, '(?ms)```.*?```', ' ') -replace 'https?://\S+', ' '
        $b = $b.ToLower() + ' ' + $base.ToLower() + ' ' + (($tags -replace '-', ' ') -join ' ')
        $anchors = @()
        foreach ($m in [regex]::Matches($b, $matcher.Pattern)) {
            if ($matcher.Lookup.ContainsKey($m.Value)) { $anchors += $matcher.Lookup[$m.Value] }
        }
        $anchors = @($anchors | Sort-Object -Unique)
        foreach ($a in $anchors) { Add-Count $anchorFreq $a }

        $status = ''; $type = ''; $date = ''
        if ($text.StartsWith('---')) {
            $end = $text.IndexOf("`n---", 3)
            if ($end -gt 0) {
                foreach ($line in ($text.Substring(0, $end) -split "`r?`n")) {
                    if ($line -match '^status\s*:\s*(\S+)') { $status = $Matches[1].ToLower() }
                    if ($line -match '^type\s*:\s*(\S+)') { $type = $Matches[1].ToLower() }
                    if ($line -match '^date\s*:\s*(\d{4})') { $date = $Matches[1] }
                }
            }
        }
        if (-not $date -and $rel -match '^(\d{4})') { $date = $Matches[1] }

        $title = ($base -replace '[|\\/:*?"<>]+', ' ' -replace '[\t\r\n]+', ' ').Trim()
        $rows.Add((($rel, $title, $date, $status, $type, $top, $sub, ($tags -join ','), ($anchors -join ','), $links) -join "`t"))
    }

    Write-Tsv -Path (Join-Path $Out 'note_features.tsv') -Lines (@("path`ttitle`tyear`tstatus`ttype`ttop`tsub`ttags`tanchors`tlinks") + $rows)

    if ($Raw) {
        Write-RankedTable $tagFreq $Out 'tags.tsv' 'tag' 'notes' $Limit
        Write-RankedTable $anchorFreq $Out 'anchors.tsv' 'anchor' 'mentions' $Limit
        Write-RankedTable $linkFreq $Out 'links.tsv' 'target' 'count' $Limit
        Write-RankedTable $titleBi $Out 'title_bigrams.tsv' 'bigram' 'notes' $Limit
        Write-RankedTable $titleTri $Out 'title_trigrams.tsv' 'trigram' 'notes' $Limit
        Write-RankedTable $folderFreq $Out 'folders.tsv' 'folder' 'notes' $Limit
        Write-RankedTable $subFolderFreq $Out 'subfolders.tsv' 'folder' 'notes' $Limit
        Write-RankedTable $typeFreq $Out 'types.tsv' 'type' 'notes' $Limit
        Write-RankedTable $statusFreq $Out 'status.tsv' 'status' 'notes' $Limit
        Write-RankedTable $platformFreq $Out 'platforms.tsv' 'platform' 'notes' $Limit

        $pairRows = @()
        foreach ($k in $pairFreq.Keys) {
            $ab = $k -split "`t"
            $c = [double]$pairFreq[$k]
            $a = [double]$tagFreq[$ab[0]]; $b = [double]$tagFreq[$ab[1]]
            $denom = $a + $b - $c
            $j = if ($denom -gt 0) { [math]::Round($c / $denom, 4) } else { 0 }
            $pairRows += "$k`t$c`t$j"
        }
        $pairRows = @($pairRows | Sort-Object { [double](($_ -split "`t")[2]) } -Descending |
                      Select-Object -First ($Limit * 2))
        Write-Tsv -Path (Join-Path $Out 'pairs.tsv') -Lines (@("tag_a`tTag_b`ttag_cooccurrence`tjaccard") + $pairRows)
        Write-Tsv -Path (Join-Path $Out 'notes.tsv') -Lines (@("path`ttags`tlink_count`ttop_folder`tsubfolder") + $rows)
    }

    return [pscustomobject]@{
        Scanned = $scanned
        TaggedNotes = $taggedNotes
        TagAssignments = $tagAssignments
        UniqueTags = $tagFreq.Count
        LinkedNotes = $linkedNotes
        UniqueLinkTargets = $linkFreq.Count
        Anchors = @($anchorNames).Count
    }
}

function Get-FocusRows {
    param([object[]]$Rows, [hashtable]$Matcher)
    foreach ($r in $Rows) {
        $t = $r.title.ToLower() + ' ' + (($r.tags -split ',' | ForEach-Object { $_ -replace '-', ' ' }) -join ' ')
        $focus = @()
        foreach ($m in [regex]::Matches($t, $Matcher.Pattern)) {
            if ($Matcher.Lookup.ContainsKey($m.Value)) { $focus += $Matcher.Lookup[$m.Value] }
        }
        $r | Add-Member -NotePropertyName focus -NotePropertyValue (@($focus | Sort-Object -Unique) -join ',') -Force
        $r
    }
}

function Invoke-Clusters {
    param([string]$Root, [string]$Out, [int]$SinceYear)

    $rows = @(Import-Csv -Path (Join-Path $Out 'note_features.tsv') -Delimiter "`t")
    $matcher = New-AnchorMatcher -Names (Get-VaultAnchors -Root $Root)
    $rows = @(Get-FocusRows -Rows $rows -Matcher $matcher)
    $noise = Get-NoisePattern
    $defs = Get-ClusterDefinitions
    $results = @()

    foreach ($name in $defs.Keys) {
        $aSet = @($defs[$name].anchors -split '\|' | ForEach-Object { $_.Trim().ToLower() })
        $tSet = @($defs[$name].tags -split '\|' | ForEach-Object { $_.Trim().ToLower() })
        $matched = @(); $hard = @(); $tagCounter = @{}; $anchorCounter = @{}; $years = @()
        $prod = 0; $draft = 0; $recent = 0; $linkSum = 0

        foreach ($r in $rows) {
            if ($r.title -match $noise) { continue }
            $rt = if ($r.tags) { @($r.tags -split ',') } else { @() }
            $ra = if ($r.focus) { @($r.focus.ToLower() -split ',') } else { @() }
            $hitT = @($rt | Where-Object { $tSet -contains $_ })
            $hitA = @($ra | Where-Object { $aSet -contains $_ })
            if ($hitT.Count -eq 0 -and $hitA.Count -eq 0) { continue }

            $matched += $r
            if ($hitT.Count -ge 2 -or ($hitT.Count -ge 1 -and $hitA.Count -ge 1) -or $hitA.Count -ge 2) { $hard += $r }
            foreach ($x in $hitT) { Add-Count $tagCounter $x }
            foreach ($x in $hitA) { Add-Count $anchorCounter $x }
            if ($r.year -match '^\d{4}$') {
                $years += [int]$r.year
                if ([int]$r.year -ge $SinceYear) { $recent++ }
            }
            if ($r.top -in @('Project', 'Share', 'StoryLine', 'Schedule')) { $prod++ }
            if ($r.status -match '^s[1234]') { $draft++ }
            $linkSum += [int]$r.links
        }

        $topTags = (@($tagCounter.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 12 |
                      ForEach-Object { "$($_.Key):$($_.Value)" })) -join ' '
        $topAnchors = (@($anchorCounter.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 10 |
                         ForEach-Object { "$($_.Key):$($_.Value)" })) -join ' '
        $samples = (@($matched | Sort-Object { [int]$_.links } -Descending | Select-Object -First 10 |
                       ForEach-Object { $_.title })) -join ' | '
        $ymed = if ($years.Count -gt 0) { [int](($years | Sort-Object)[[int]($years.Count / 2)]) } else { 0 }

        $results += [pscustomobject]@{
            Cluster = $name
            Notes = $matched.Count
            HardCore = $hard.Count
            Production = $prod
            WorkflowS1toS4 = $draft
            SinceYear = $recent
            AvgLinks = [math]::Round($linkSum / [math]::Max(1, $matched.Count), 1)
            MedianYear = $ymed
            DistinctTags = $tagCounter.Count
            TopTags = $topTags
            TopTitleRoots = $topAnchors
            SampleTitles = $samples
        }
    }

    $results = @($results | Sort-Object HardCore -Descending)
    $fields = 'Cluster','Notes','HardCore','Production','WorkflowS1toS4','SinceYear','AvgLinks','MedianYear','DistinctTags','TopTags','TopTitleRoots','SampleTitles'
    $lines = @(($fields -join "`t"))
    foreach ($r in $results) {
        $vals = foreach ($f in $fields) { ([string]$r.$f) -replace '[\t\r\n]+', ' ' }
        $lines += ($vals -join "`t")
    }
    Write-Tsv -Path (Join-Path $Out 'refined_clusters.tsv') -Lines $lines
    Write-JsonUtf8 -Object $results -Path (Join-Path $Out 'refined_clusters.json')
    return $results
}

function Invoke-Overlap {
    param([string]$Root, [string]$Out)

    $rows = @(Import-Csv -Path (Join-Path $Out 'note_features.tsv') -Delimiter "`t")
    $matcher = New-AnchorMatcher -Names (Get-VaultAnchors -Root $Root)
    $rows = @(Get-FocusRows -Rows $rows -Matcher $matcher)
    $noise = Get-NoisePattern
    $defs = Get-ClusterDefinitions
    $members = @{}

    foreach ($r in $rows) {
        if ($r.title -match $noise) { continue }
        $text = $r.title.ToLower() + ' ' + (($r.tags -split ',' | ForEach-Object { $_ -replace '-', ' ' }) -join ' ')
        $focus = @()
        foreach ($m in [regex]::Matches($text, $matcher.Pattern)) {
            if ($matcher.Lookup.ContainsKey($m.Value)) { $focus += $matcher.Lookup[$m.Value].ToLower() }
        }
        $focus = @($focus | Sort-Object -Unique)
        $rt = @($r.tags -split ',' | Where-Object { $_ })

        foreach ($name in $defs.Keys) {
            $as = @($defs[$name].anchors -split '\|' | ForEach-Object { $_.Trim().ToLower() })
            $ts = @($defs[$name].tags -split '\|')
            $ha = @($focus | Where-Object { $as -contains $_ })
            $ht = @($rt | Where-Object { $ts -contains $_ })
            if ($ha.Count -gt 0 -or $ht.Count -gt 0) {
                if (-not $members.ContainsKey($name)) { $members[$name] = @() }
                $members[$name] += $r
            }
        }
    }

    $names = @($defs.Keys)
    $pairs = @()
    for ($i = 0; $i -lt $names.Count; $i++) {
        for ($j = $i + 1; $j -lt $names.Count; $j++) {
            $a = $names[$i]; $b = $names[$j]
            $sb = @($members[$b] | ForEach-Object { $_.path })
            $shared = @($members[$a] | Where-Object { $sb -contains $_.path })
            if ($shared.Count -lt 8) { continue }
            $na = if ($members.ContainsKey($a)) { @($members[$a]).Count } else { 0 }
            $nb = if ($members.ContainsKey($b)) { @($members[$b]).Count } else { 0 }
            $denom = $na + $nb - $shared.Count
            $jac = if ($denom -gt 0) { [math]::Round($shared.Count / $denom, 3) } else { 0 }
            $pairs += [pscustomobject]@{
                A = $a; B = $b; Overlap = $shared.Count; Jaccard = $jac
                SampleBridges = (@($shared | Sort-Object { [int]$_.links } -Descending |
                                   Select-Object -First 6 | ForEach-Object { $_.title })) -join ' | '
            }
        }
    }

    $pairs = @($pairs | Sort-Object Overlap -Descending)
    $lines = @("A`tB`tOverlap`tJaccard`tSampleBridges")
    foreach ($p in $pairs) {
        $lines += (($p.A, $p.B, $p.Overlap, $p.Jaccard, $p.SampleBridges) -join "`t")
    }
    Write-Tsv -Path (Join-Path $Out 'cluster_overlap.tsv') -Lines $lines
    Write-JsonUtf8 -Object $pairs -Path (Join-Path $Out 'cluster_overlap.json')
    return $pairs
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
$vaultRoot = Get-CleanPath -Path $VaultPath
if (-not (Test-Path -LiteralPath $vaultRoot -PathType Container)) {
    throw "VaultPath does not exist: $vaultRoot"
}
if (-not (New-Item -ItemType Directory -Path $OutputDir -Force -ErrorAction SilentlyContinue)) {
    throw "Cannot create OutputDir: $OutputDir"
}
$outDir = Get-CleanPath -Path $OutputDir

Write-Host "Vault:  $vaultRoot"
Write-Host "Output: $outDir"
Write-Host 'Scanning notes...'
$scan = Invoke-Scan -Root $vaultRoot -Out $outDir -Limit $TopN -Raw:$IncludeRawSignals
Write-Host ('Scanned {0} notes; {1} tagged; {2} unique tags; {3} link targets.' -f $scan.Scanned, $scan.TaggedNotes, $scan.UniqueTags, $scan.UniqueLinkTargets)

Write-Host 'Building clusters...'
$clusters = Invoke-Clusters -Root $vaultRoot -Out $outDir -SinceYear $SinceYear
Write-Host 'Finding cluster junctions...'
$overlap = Invoke-Overlap -Root $vaultRoot -Out $outDir

$summary = @()
$summary += "Vault: $vaultRoot"
$summary += "Generated: $(Get-Date -Format o)"
$summary += "Scanned=$($scan.Scanned) TaggedNotes=$($scan.TaggedNotes) TagAssignments=$($scan.TagAssignments) UniqueTags=$($scan.UniqueTags) Anchors=$($scan.Anchors) LinkedNotes=$($scan.LinkedNotes) UniqueLinkTargets=$($scan.UniqueLinkTargets)"
$summary += ''
$summary += ($clusters | Format-Table Cluster,Notes,HardCore,Production,WorkflowS1toS4,SinceYear,AvgLinks,MedianYear,DistinctTags -AutoSize | Out-String -Width 250)
$summary += ''
$summary += ($overlap | Select-Object -First 20 | Format-Table A,B,Overlap,Jaccard -AutoSize | Out-String -Width 250)
Write-Tsv -Path (Join-Path $outDir 'summary.txt') -Lines $summary

Write-Host ''
Write-Host ($clusters | Format-Table Cluster,Notes,HardCore,Production,SinceYear,MedianYear -AutoSize | Out-String -Width 250)
Write-Host "Done. Files written to $outDir"

if ($PassThru) {
    return [pscustomobject]@{ Scan = $scan; Clusters = $clusters; Overlap = $overlap; OutputDir = $outDir }
}
