#!/usr/bin/env python3
"""
Extract PERSON named entities from markdown using spaCy.

Reports real people -- both personal contacts and public figures -- one row per
person, with name variants merged into a canonical form.

Usage:
    python3 MarkdownTools/extract-names-ner.py /path/to/markdown
    python3 MarkdownTools/extract-names-ner.py notes.md --out outputs/people.csv
    cat notes.md | python3 MarkdownTools/extract-names-ner.py -
    python3 MarkdownTools/extract-names-ner.py . --rejected outputs/not-people.csv

Requires `spacy` and an English model:
    pip3 install spacy && python3 -m spacy download en_core_web_sm

Optional, and used when present to improve accuracy:
    nltk            -- `names` corpus, used as a given-name gazetteer
    pyspellchecker  -- English dictionary, used to reject common-noun phrases
    PyYAML          -- only for reading a `--config` lexicon override

Why this is not just "run NER and print PERSON": markdown carries a lot of text
that is not prose. YAML frontmatter, headings, hashtags, Dataview inline fields,
wikilinks and code all get mislabelled as PERSON when handed to a model raw --
a vault whose every note begins `author: Justin Hitt` will report that name once
per file, which is a file count and not a mention count. Equally, a blanket strip
of everything non-prose is wrong too: in a Zettelkasten, people legitimately live
in headings and wikilinks. So each region of the document is handled according to
what it actually contains, and every candidate then has to pass a name test.
"""

import os
import re
import sys
import csv
import argparse
from collections import Counter, defaultdict

try:
    import spacy
except Exception:
    print("spaCy is not installed. Please run: pip3 install spacy", file=sys.stderr)
    sys.exit(2)


# --------------------------------------------------------------------------- #
# Lexicons
#
# Defaults live here so the script is self-contained and runs with no data
# files. Any of these sets can be replaced or extended with `--config FILE`
# (YAML), which is the centralized-configuration hook for the wider toolset.
# --------------------------------------------------------------------------- #

# Frontmatter keys whose value IS a person. An allowlist, deliberately: the
# noisiest false positives came from sibling keys such as `status: S1-Draft`
# and `service: Podcast Producer`.
PERSON_KEYS = {"author", "curator", "interviewer", "contact"}

# Publishing-channel and content-type words. Tested as one combined set, but
# kept apart for readability. Together they form a productive grammar --
# channel x content -- so unseen combinations ("Mastodon Reply") are caught as
# well as the ones already in the corpus.
CHANNEL_WORDS = {
    "email", "e-mail", "facebook", "reddit", "youtube", "linkedin", "nextdoor",
    "twitter", "zoom", "spreaker", "substack", "instagram", "tiktok", "medium",
    "slack", "discord", "whatsapp", "telegram", "mastodon", "pinterest",
    "snapchat", "aweber", "godaddy", "podio", "asana", "infusionsoft",
    "wordpress", "hubspot", "quickbooks", "shoeboxed", "looker", "adobe",
}
CONTENT_WORDS = {
    "reply", "replies", "message", "broadcast", "comment", "comments",
    "podcast", "video", "newsletter", "draft", "short", "shorts",
    "description", "studio", "clips", "clip", "post", "thread", "transcript",
    "history", "keyword", "keywords", "scope", "required", "method", "meta",
    "image", "summary", "excerpt", "outline", "title", "subject", "body",
    "link", "url", "tag", "tags", "unsubscribed", "attendance", "calendar",
    "guidelines", "baseline", "deliverables", "persona", "quotes", "record",
    "inventory", "schedule", "advisory", "purpose", "page", "template",
    "metadata", "rolodex", "glossary", "roles", "variance", "types",
}

# Party and role nouns. Capitalized throughout contracts and agreements, where
# a model reads them as the name of whoever is filling the role.
LEGAL_WORDS = {
    "lessee", "lessor", "seller", "purchaser", "tenant", "landlord",
    "borrower", "lender", "grantor", "grantee", "licensee", "licensor",
    "contractor", "subcontractor", "vendor", "supplier", "signature",
    "signatures", "witness", "guarantor", "assignee", "assignor",
    "beneficiary", "trustee", "executor", "claimant", "respondent",
}

# Frontmatter key names seen in the corpus. A Title-Case phrase built from one
# of these ("Workflow Types", "Status Types") is a metadata label, not a person.
FIELD_WORDS = {
    "workflow", "status", "type", "catalog", "platform", "service", "channel",
    "priority", "campaign", "serial", "domain", "hostname", "plugin",
    "permalink", "original", "created", "updated", "due", "scheduled",
    "published", "completion", "aliases", "cdir", "source-url",
}

# Trailing address tokens. Two-letter state codes ("Charlotte NC") are already
# excluded by the ALL-CAPS rule in the shape test; these are the sentence-case
# ones that slip past it.
STREET_WORDS = {
    "st", "street", "ct", "court", "ave", "avenue", "rd", "road", "ln", "lane",
    "blvd", "boulevard", "dr", "drive", "way", "pl", "place", "pkwy", "hwy",
    "cir", "circle", "ter", "terrace", "trl", "trail", "sq", "square",
}

# Business and byline words. A person name followed by one of these is that
# person wearing a hat -- "Justin Hitt Publisher", "Justin Hitt Strategic
# Relations" -- so the suffix is stripped and the mention credited to the person.
ROLE_WORDS = {
    "publisher", "publishing", "analyst", "consultant", "consulting", "editor",
    "editorial", "business", "strategic", "relations", "blog", "media",
    "group", "associates", "partners", "enterprises", "ventures", "press",
    "company", "co", "llc", "inc", "incorporated", "corp", "corporation",
    "ltd", "holdings", "studios", "agency", "advisors", "mastermind",
    "seminar", "academy", "institute", "foundation", "trust", "network",
}

# Stripped before the shape test so a credential does not disqualify a real
# name: "David D Jones DDS" -> "David D Jones".
HONORIFICS = {"mr", "mrs", "ms", "miss", "dr", "prof", "professor", "rev",
              "sen", "rep", "sir", "madam", "hon", "capt", "col", "gen", "lt"}
CREDENTIALS = {"jr", "sr", "ii", "iii", "iv", "md", "dds", "phd", "esq", "cpa",
               "mba", "dvm", "rn", "do", "jd", "msw", "lcsw", "pe", "cfa"}

# A single name token. Permissive about the shapes real names take -- dotted
# initials (E.J.), Mc/Mac, O', one internal capital (MaryEllen), hyphenated
# givens (Li-Yu) -- because a naive ^[A-Z][a-z]+$ discards Li-Yu Chen,
# Yo-Ray Hitt, John McCormick, MaryEllen Tribby and E.J. Troy. Still rejects
# ALL-CAPS (HITT, MOC, NC, GPT, BS) and anything with a digit.
NAME_TOKEN = re.compile(
    r"""^(?:
          (?:[A-ZÀ-ÖØ-Þ]\.){1,3}
        | Ma?c[A-ZÀ-ÖØ-Þ][a-zß-öø-ÿ']+
        | O'[A-ZÀ-ÖØ-Þ][a-zß-öø-ÿ']+
        | [A-ZÀ-ÖØ-Þ][a-zß-öø-ÿ']*
          (?:[A-ZÀ-ÖØ-Þ][a-zß-öø-ÿ']+)?
          (?:-[A-Za-zÀ-ÖØ-Þß-öø-ÿ][a-zß-öø-ÿ']*)*
        | [A-ZÀ-ÖØ-Þ]\.?
        )$""",
    re.X,
)

# Corpus count above which a word is "ordinary English" rather than a name.
# Note this is a raw occurrence count, not a normalized frequency -- which is
# what pyspellchecker's word_frequency actually returns.
#
# The test is on the RAREST token, not on all of them. Requiring every token to
# be absent from the dictionary loses Barack Obama, Kamala Harris, Tai Goodwin
# and Mao Zedong, because a web-derived word list knows those names perfectly
# well. Asking instead whether even the least common token is still a frequent
# English word separates "Implementation Schedule" from "Barack Obama".
COMMON_FLOOR = 400

MAX_CHUNK = 100_000  # characters per document handed to spaCy


# --------------------------------------------------------------------------- #
# Markdown region handling
# --------------------------------------------------------------------------- #

FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)
FM_KEY_RE = re.compile(r"^([A-Za-z_][\w -]*):[ \t]*(.*)$")
FM_ITEM_RE = re.compile(r"^[ \t]+-[ \t]+(.+?)[ \t]*$")

FENCED_RE = re.compile(r"^[ \t]*(```|~~~).*?^[ \t]*\1[ \t]*$", re.S | re.M)
COMMENT_RE = re.compile(r"%%.*?%%", re.S)
PLACEHOLDER_RE = re.compile(r"\{\{[^}]*\}\}")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
DATAVIEW_RE = re.compile(r"\[[^\]\[]*::[^\]\[]*\]")
WIKILINK_RE = re.compile(r"!?\[\[([^\]\[|#]*)(?:#[^\]\[|]*)?(?:\|([^\]\[]*))?\]\]")
MDLINK_RE = re.compile(r"!?\[([^\]\[]*)\]\([^)]*\)")
URL_RE = re.compile(r"(?:https?://|www\.)\S+")
HEADING_RE = re.compile(r"^[ \t]{0,3}#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$", re.M)
HASHTAG_RE = re.compile(r"(?<!\w)#[\w/-]+")
TASKBOX_RE = re.compile(r"^[ \t]*[-*+][ \t]*\[[ xX/\->]\][ \t]*", re.M)
LISTMARK_RE = re.compile(r"^[ \t]*(?:[-*+]|\d+\.)[ \t]+", re.M)


def split_frontmatter(text):
    """Return (frontmatter_body_or_None, rest_of_document)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def unwrap_value(value):
    """Strip quoting and wikilink brackets from a frontmatter scalar.

    Values in the wild look like `Justin Hitt`, `"[[Frank Kern]]"` and
    `[[Note|Display]]`, so all three have to reduce to a bare name.
    """
    v = value.strip().strip("\"'").strip()
    m = WIKILINK_RE.fullmatch(v)
    if m:
        v = m.group(2) or m.group(1)
    return " ".join(v.split())


def frontmatter_people(fm, person_keys):
    """Pull values of person-valued keys out of frontmatter.

    Parsed by hand rather than with PyYAML: Obsidian templates contain
    `date: {{date:YYYY-MM-DD}}`, which is not valid YAML and would abort the
    parse for the whole file. Only scalars and simple `- item` lists are needed.
    """
    found = []
    if not fm:
        return found
    lines = fm.splitlines()
    for i, line in enumerate(lines):
        m = FM_KEY_RE.match(line)
        if not m:
            continue
        key, raw = m.group(1).strip().lower(), m.group(2).strip()
        if key not in person_keys:
            continue
        if raw:
            found.append(unwrap_value(raw))
            continue
        for follow in lines[i + 1:]:
            item = FM_ITEM_RE.match(follow)
            if not item:
                break
            found.append(unwrap_value(item.group(1)))
    return [f for f in found if f]


def split_regions(body):
    """Reduce a document body to (wikilink_targets, heading_texts, prose).

    Order matters. Code and comments go first so their contents cannot be
    mistaken for structure; wikilinks are resolved before headings so that a
    heading like `## [[Pete Moyer]]` yields a clean heading string.
    """
    t = FENCED_RE.sub(" ", body)
    t = COMMENT_RE.sub(" ", t)
    t = PLACEHOLDER_RE.sub(" ", t)
    t = INLINE_CODE_RE.sub(" ", t)
    t = DATAVIEW_RE.sub(" ", t)

    targets = []

    def _wikilink(m):
        target, display = m.group(1), m.group(2)
        if target:
            targets.append(" ".join(target.split()))
        return " " + (display or target or "") + " "

    t = WIKILINK_RE.sub(_wikilink, t)
    t = MDLINK_RE.sub(r"\1", t)
    t = URL_RE.sub(" ", t)

    headings = [" ".join(h.split()) for h in HEADING_RE.findall(t)]
    t = HEADING_RE.sub(" ", t)

    t = HASHTAG_RE.sub(" ", t)
    t = TASKBOX_RE.sub("", t)
    t = LISTMARK_RE.sub("", t)
    t = re.sub(r"[*_~`>|\[\]]+", " ", t)

    return targets, headings, t


def chunk(text, limit=MAX_CHUNK):
    """Split oversized text on blank lines so spaCy's length cap is never hit."""
    if len(text) <= limit:
        return [text]
    out, buf = [], []
    size = 0
    for para in text.split("\n\n"):
        # A single paragraph can exceed the limit on its own -- generated
        # tables, minified data pasted into a note -- so hard-split it.
        while len(para) > limit:
            out.append(para[:limit])
            para = para[limit:]
        if size + len(para) > limit and buf:
            out.append("\n\n".join(buf))
            buf, size = [], 0
        buf.append(para)
        size += len(para) + 2
    if buf:
        out.append("\n\n".join(buf))
    return out


# --------------------------------------------------------------------------- #
# Name validation
# --------------------------------------------------------------------------- #

SURFACE_STRIP = " \t\r\n*_`~#\"'.,;:!?()[]{}<>"


def normalize_surface(raw):
    """Tidy an entity string, or return None if it cannot be a name."""
    if not raw:
        return None
    s = raw.replace("**", " ").replace("__", " ")
    s = " ".join(s.split()).strip(SURFACE_STRIP)
    s = re.sub(r"(?:['’`])[sS]$", "", s)          # possessive
    s = " ".join(s.split()).strip(SURFACE_STRIP)
    if not s or len(s) > 60:
        return None
    if any(ch.isdigit() for ch in s):
        return None
    if any(ch in s for ch in "@/:\\"):
        return None
    return s


def strip_affixes(tokens):
    """Drop leading honorifics and trailing credentials."""
    out = list(tokens)
    while out and out[0].lower().strip(".") in HONORIFICS:
        out.pop(0)
    while out and out[-1].lower().strip(".") in CREDENTIALS:
        out.pop()
    return out


def strip_role_suffix(tokens):
    """Fold "Justin Hitt Publisher" down to "Justin Hitt"."""
    out = list(tokens)
    while len(out) > 2 and out[-1].lower().strip(".") in ROLE_WORDS:
        out.pop()
    return out


class Validator:
    """Decides whether a candidate string names a person.

    Positive evidence is tested before any dictionary-based rejection. That
    ordering is not cosmetic: pyspellchecker's frequency list is corpus-derived
    and contains proper names, so a dictionary-first rule throws out Thomas
    Jefferson, Bill Gates and Gary Halbert along with the noise.
    """

    def __init__(self, given_names=None, word_freq=None, lexicons=None):
        lex = lexicons or {}
        self.given = given_names or set()
        self.freq = word_freq
        self.template = set(lex.get("channel_words", CHANNEL_WORDS)) | \
            set(lex.get("content_words", CONTENT_WORDS)) | \
            set(lex.get("legal_words", LEGAL_WORDS))
        self.fields = set(lex.get("field_words", FIELD_WORDS))
        self.streets = set(lex.get("street_words", STREET_WORDS))

    def _rarest(self, tokens):
        """Corpus count of the least common token, or None if unavailable."""
        if self.freq is None:
            return None
        counts = [self.freq[t.lower().strip(".'")] for t in tokens
                  if len(t.strip(".'")) > 1]
        return min(counts) if counts else None

    def check(self, surface):
        """Return (canonical_surface, confidence, reason).

        confidence is "high", "medium", or None when rejected -- in which case
        reason carries the rejection code.
        """
        tokens = strip_role_suffix(strip_affixes(surface.split()))
        if len(tokens) < 2:
            return None, None, "single-token"
        if not all(NAME_TOKEN.match(t) for t in tokens):
            return None, None, "shape"

        name = " ".join(tokens)
        low = [t.lower().strip(".'") for t in tokens]

        if any(t in self.template for t in low):
            return name, None, "template-term"
        if low[-1] in self.streets:
            return name, None, "address"
        if any(t in self.fields for t in low):
            return name, None, "field-name"

        if low[0] in self.given:
            return name, "high", "given-name"

        rarest = self._rarest(tokens)
        if rarest is None or rarest < COMMON_FLOOR:
            return name, "medium", "non-dictionary"

        return name, None, "common-words"

    def token_could_be_name(self, token):
        """Loose test used to decide whether a lone token is worth resolving."""
        if not NAME_TOKEN.match(token):
            return False
        low = token.lower().strip(".'")
        return low not in self.template and low not in self.fields \
            and low not in self.streets and len(low) > 1


def load_given_names(extra_path=None, quiet=False):
    """Given-name gazetteer, from NLTK's `names` corpus plus an optional file."""
    out = set()
    try:
        from nltk.corpus import names as nltk_names
        out |= {w.lower() for w in nltk_names.words()}
    except Exception:
        try:
            import nltk
            nltk.download("names", quiet=True)
            from nltk.corpus import names as nltk_names
            out |= {w.lower() for w in nltk_names.words()}
        except Exception:
            if not quiet:
                print("Note: NLTK 'names' corpus unavailable; relying on the "
                      "dictionary test alone (lower recall on common-word "
                      "names). Install with: pip3 install nltk", file=sys.stderr)
    if extra_path:
        try:
            with open(extra_path, "r", encoding="utf-8") as fh:
                for line in fh:
                    w = line.strip().lower()
                    if w and not w.startswith("#"):
                        out.add(w)
        except Exception as exc:
            print(f"Warning: could not read --names {extra_path}: {exc}",
                  file=sys.stderr)
    return out


def load_word_freq(quiet=False):
    """English dictionary used only to reject all-common-word phrases."""
    try:
        from spellchecker import SpellChecker
        return SpellChecker(distance=1).word_frequency
    except Exception:
        if not quiet:
            print("Note: pyspellchecker unavailable; common-noun phrases such "
                  "as 'Implementation Schedule' cannot be rejected. Install "
                  "with: pip3 install pyspellchecker", file=sys.stderr)
        return None


def load_lexicons(path):
    if not path:
        return {}
    try:
        import yaml
    except Exception:
        print("Warning: --config needs PyYAML; ignoring override.", file=sys.stderr)
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        return {k: set(v) for k, v in data.items() if isinstance(v, (list, set))}
    except Exception as exc:
        print(f"Warning: could not read --config {path}: {exc}", file=sys.stderr)
        return {}


# --------------------------------------------------------------------------- #
# Tallying
# --------------------------------------------------------------------------- #

class Tally:
    """Per-surface-form evidence, kept separate until aliases are merged."""

    def __init__(self):
        self.mentions = Counter()               # prose/heading/wikilink hits
        self.frontmatter = Counter()            # files naming them in metadata
        self.files = defaultdict(set)
        self.sources = defaultdict(set)
        self.confidence = {}
        self.singles = Counter()                # lone tokens, resolved later
        self.rejected = Counter()               # (surface, reason) -> count

    def add(self, surface, confidence, path, source):
        if source == "frontmatter":
            self.frontmatter[surface] += 1
        else:
            self.mentions[surface] += 1
        self.files[surface].add(path)
        self.sources[surface].add(source)
        rank = {"medium": 1, "high": 2}
        if rank.get(confidence, 0) > rank.get(self.confidence.get(surface), 0):
            self.confidence[surface] = confidence

    def total(self, surface):
        return self.mentions[surface] + self.frontmatter[surface]


def record(tally, validator, raw, path, source):
    surface = normalize_surface(raw)
    if not surface:
        return
    tokens = surface.split()
    if len(tokens) == 1:
        if validator.token_could_be_name(tokens[0]):
            tally.singles[tokens[0]] += 1
        return
    name, confidence, reason = validator.check(surface)
    if confidence is None:
        tally.rejected[(name or surface, reason)] += 1
        return
    tally.add(name, confidence, path, source)


# --------------------------------------------------------------------------- #
# Alias merging
# --------------------------------------------------------------------------- #

def _first_key(name):
    return re.sub(r"[^a-z]", "", name.split()[0].lower())


def _last_key(name):
    return re.sub(r"[^a-z]", "", name.split()[-1].lower())


def _compatible(a, b):
    """First names match if equal, or if one is an initial of the other.

    Deliberately conservative. Merging on surname alone would collapse
    John Smith and Jane Smith into one person; requiring first-name
    compatibility keeps them apart while still folding J. Hitt, Justin W Hitt
    and Justin William Hitt together.
    """
    if a == b:
        return True
    if len(a) == 1 and b.startswith(a):
        return True
    if len(b) == 1 and a.startswith(b):
        return True
    return False


def merge_aliases(tally):
    """Cluster surface forms into people. Returns {canonical: [variants]}."""
    groups = defaultdict(list)
    for surface in tally.mentions.keys() | tally.frontmatter.keys():
        groups[_last_key(surface)].append(surface)

    clusters = {}
    for surnames in groups.values():
        surnames.sort(key=lambda s: (-tally.total(s), s))
        buckets = []
        for surface in surnames:
            key = _first_key(surface)
            for bucket in buckets:
                if any(_compatible(key, k) for k in bucket["keys"]):
                    bucket["keys"].add(key)
                    bucket["members"].append(surface)
                    break
            else:
                buckets.append({"keys": {key}, "members": [surface]})

        for bucket in buckets:
            members = bucket["members"]
            spelled = [m for m in members if len(_first_key(m)) > 1]
            pool = spelled or members
            canonical = max(pool, key=lambda s: (tally.total(s), -len(s), s))
            clusters[canonical] = [m for m in members if m != canonical]
    return clusters


def resolve_singles(tally, clusters):
    """Credit lone first/last names to a person when the match is unambiguous.

    The README asks for single-word names to be ignored, and they are never
    reported as rows. But a bare "Pete" in a note that also names Pete Moyer is
    a real mention, so it is folded in when exactly one person matches.
    """
    index = defaultdict(set)
    for canonical, variants in clusters.items():
        for form in [canonical] + variants:
            for token in form.split():
                key = re.sub(r"[^a-z]", "", token.lower())
                if len(key) > 1:
                    index[key].add(canonical)

    resolved = Counter()
    for token, count in tally.singles.items():
        key = re.sub(r"[^a-z]", "", token.lower())
        owners = index.get(key)
        if owners and len(owners) == 1:
            resolved[next(iter(owners))] += count
    return resolved


# --------------------------------------------------------------------------- #
# Scanning
# --------------------------------------------------------------------------- #

def iter_markdown(target):
    if target == "-":
        yield "<stdin>", sys.stdin.read()
        return
    if os.path.isfile(target):
        try:
            with open(target, "r", encoding="utf-8", errors="replace") as fh:
                yield target, fh.read()
        except Exception:
            pass
        return
    for dirpath, dirnames, filenames in os.walk(target):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fname in sorted(filenames):
            if not fname.lower().endswith(".md"):
                continue
            full = os.path.join(dirpath, fname)
            try:
                with open(full, "r", encoding="utf-8", errors="replace") as fh:
                    yield full, fh.read()
            except Exception:
                continue


def build_jobs(target, tally, validator, person_keys, progress):
    """Record non-NER evidence and yield (text, context) pairs for nlp.pipe.

    Frontmatter values and wikilink targets are whole-string candidates and go
    straight to the validator -- running a model over a two-word fragment is
    less reliable than testing the string directly. Prose and heading text do
    need NER, so they are handed back for batching.
    """
    count = 0
    for count, (path, text) in enumerate(iter_markdown(target), 1):
        if progress and count % 500 == 0:
            print(f"  scanned {count} files...", file=sys.stderr)

        fm, body = split_frontmatter(text)
        for person in frontmatter_people(fm, person_keys):
            record(tally, validator, person, path, "frontmatter")

        targets, headings, prose = split_regions(body)
        for target_text in targets:
            record(tally, validator, target_text, path, "wikilink")

        for piece in chunk(prose):
            if piece.strip():
                yield piece, (path, "prose")
        if headings:
            for piece in chunk("\n".join(headings)):
                if piece.strip():
                    yield piece, (path, "heading")
    if progress:
        print(f"  scanned {count} files total.", file=sys.stderr)


def write_people(rows, outpath):
    directory = os.path.dirname(outpath)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(outpath, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        writer.writerow(["name", "mentions", "frontmatter", "files",
                         "confidence", "evidence", "variants"])
        writer.writerows(rows)


def write_rejected(tally, outpath):
    directory = os.path.dirname(outpath)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(outpath, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        writer.writerow(["candidate", "count", "reason"])
        for (surface, reason), count in sorted(
                tally.rejected.items(), key=lambda x: (-x[1], x[0][0])):
            writer.writerow([surface, count, reason])


def load_model(preferred=None):
    """Load an English pipeline with only the components NER needs."""
    exclude = ["parser", "tagger", "attribute_ruler", "lemmatizer"]
    candidates = [preferred] if preferred else []
    candidates += ["en_core_web_lg", "en_core_web_md", "en_core_web_sm"]
    for name in candidates:
        if not name:
            continue
        try:
            return spacy.load(name, exclude=exclude), name
        except Exception:
            continue
    print("Could not load an English model. Run: "
          "python3 -m spacy download en_core_web_sm", file=sys.stderr)
    sys.exit(3)


def main():
    parser = argparse.ArgumentParser(
        description="Extract PERSON named entities from markdown.")
    parser.add_argument("target", nargs="?", default=".",
                        help="Directory to walk, a single .md file, or - for stdin")
    parser.add_argument("--out", default="outputs/people.csv",
                        help="CSV output path (default: outputs/people.csv)")
    parser.add_argument("--rejected", metavar="PATH",
                        help="Also write discarded candidates with a reason code")
    parser.add_argument("--min-count", type=int, default=1,
                        help="Minimum total evidence to include (default: 1)")
    parser.add_argument("--confidence", choices=["high", "medium"],
                        default="medium",
                        help="Lowest confidence to report (default: medium)")
    parser.add_argument("--model", help="spaCy model name to prefer")
    parser.add_argument("--names", metavar="PATH",
                        help="Extra given names, one per line, to raise confidence")
    parser.add_argument("--config", metavar="PATH",
                        help="YAML lexicon override (channel/content/field/street words)")
    parser.add_argument("--batch-size", type=int, default=64,
                        help="Documents per spaCy batch (default: 64)")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress")
    args = parser.parse_args()

    if args.target != "-" and not os.path.exists(args.target):
        print(f"Error: no such file or directory: {args.target}", file=sys.stderr)
        sys.exit(1)

    progress = not args.quiet
    if progress:
        print("Loading spaCy model...", file=sys.stderr)
    nlp, model_name = load_model(args.model)
    if progress:
        print(f"Model loaded: {model_name}", file=sys.stderr)

    lexicons = load_lexicons(args.config)
    validator = Validator(
        given_names=load_given_names(args.names, quiet=args.quiet),
        word_freq=load_word_freq(quiet=args.quiet),
        lexicons=lexicons,
    )
    person_keys = lexicons.get("person_keys", PERSON_KEYS)

    tally = Tally()
    if progress:
        print("Scanning files...", file=sys.stderr)
    jobs = build_jobs(args.target, tally, validator, person_keys, progress)
    for doc, (path, source) in nlp.pipe(jobs, as_tuples=True,
                                        batch_size=args.batch_size):
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                record(tally, validator, ent.text, path, source)

    if progress:
        print("Merging name variants...", file=sys.stderr)
    clusters = merge_aliases(tally)
    resolved = resolve_singles(tally, clusters)

    floor = {"high": 2, "medium": 1}[args.confidence]
    rank = {"high": 2, "medium": 1}
    rows = []
    for canonical, variants in clusters.items():
        forms = [canonical] + variants
        mentions = sum(tally.mentions[f] for f in forms) + resolved[canonical]
        frontmatter = sum(tally.frontmatter[f] for f in forms)
        files = set()
        sources = set()
        best = None
        for f in forms:
            files |= tally.files[f]
            sources |= tally.sources[f]
            if rank.get(tally.confidence.get(f), 0) > rank.get(best, 0):
                best = tally.confidence.get(f)
        if resolved[canonical]:
            sources.add("alias")
        if rank.get(best, 0) < floor:
            continue
        if mentions + frontmatter < args.min_count:
            continue
        rows.append([canonical, mentions, frontmatter, len(files), best,
                     "|".join(sorted(sources)), "; ".join(sorted(variants))])

    rows.sort(key=lambda r: (-r[1], -r[2], r[0]))
    write_people(rows, args.out)
    if args.rejected:
        write_rejected(tally, args.rejected)

    if progress:
        dropped = sum(tally.rejected.values())
        print(f"People: {len(rows)}  |  candidates rejected: {dropped}",
              file=sys.stderr)
        print(f"CSV written to: {args.out}", file=sys.stderr)
        if args.rejected:
            print(f"Rejects written to: {args.rejected}", file=sys.stderr)


if __name__ == "__main__":
    main()
