VAULT CLUSTER ANALYSIS - usage
==============================

One file, no dependencies beyond Windows PowerShell 5.1 or PowerShell 7.
Reads Markdown only. Writes nothing into the vault unless you point -OutputDir
at a folder inside it (not recommended); default output is %TEMP%.

RUN
---
From this folder:

  powershell -ExecutionPolicy Bypass -File .\VaultClusterAnalysis.ps1 -VaultPath "C:\Users\hittj\Github\obsidian"

Against another vault, with raw signal tables and a different momentum year:

  powershell -ExecutionPolicy Bypass -File .\VaultClusterAnalysis.ps1 -VaultPath "D:\notes" -OutputDir "D:\analysis" -IncludeRawSignals -SinceYear 2025

PARAMETERS
----------
  -VaultPath          Root of the vault. Default: current directory.
  -OutputDir          Where results go. Default: %TEMP%\VaultClusterAnalysis.
  -SinceYear          Year used for the "SinceYear" momentum column. Default 2024.
  -TopN               Row limit for ranked raw-signal tables. Default 500.
  -IncludeRawSignals  Also write tag, anchor, link, n-gram, folder and pair tables.
  -PassThru           Return scan/cluster/overlap objects to the caller.

OUTPUT
------
  note_features.tsv     One row per note: path, title, year, status, type, top
                        folder, subfolder, tags, roots, wikilink count.
  refined_clusters.tsv  Ranked clusters with counts, momentum, top tags, roots,
                        and sample titles.
  refined_clusters.json Same data as JSON.
  cluster_overlap.tsv   Cluster-to-cluster junctions and bridge note titles.
  cluster_overlap.json  Same data as JSON.
  summary.txt           Console summary saved as text.

  With -IncludeRawSignals: tags.tsv, anchors.tsv, links.tsv, title_bigrams.tsv,
  title_trigrams.tsv, folders.tsv, subfolders.tsv, types.tsv, status.tsv,
  platforms.tsv, pairs.tsv (tag co-occurrence with Jaccard), notes.tsv.

HOW IT DECIDES MEMBERSHIP
-------------------------
Root keywords come from the filenames in Taxonomy\Keywords. A Zettelkasten
timestamp prefix and a trailing "Root" are stripped. If that folder is absent,
the script warns and uses tags alone.

A note matches a cluster if any cluster tag or root keyword appears in its
frontmatter tags or title. Body mentions are deliberately NOT used for cluster
membership because long notes collect unrelated roots and inflate counts.
Body mentions are used only in the optional anchors.tsv signal table.

"HardCore" requires two independent signals: two matching tags, or one tag plus
one root in title/tags, or two roots in title/tags.

Resumes, invoices, chat logs, daily-note titles, and workflow scaffolding are
excluded by Get-NoisePattern. Edit that function to change what is filtered.

EDITING CLUSTERS
----------------
Open the script and edit the Get-ClusterDefinitions function near the top.
Each cluster has "anchors" (root keyword names) and "tags" (YAML tags), both
pipe-delimited. Add a cluster by adding one entry. No other edits needed.

PERFORMANCE
-----------
About 26,700 notes / 100 MB took a few minutes on Windows PowerShell 5.1.
Output folder is excluded automatically from the scan.
