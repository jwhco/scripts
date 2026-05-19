#!/usr/bin/env python3

import argparse
import html
import os
import random
import re
import shutil
import subprocess
import threading
import time
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from urllib.request import urlopen

DEFAULT_CONCURRENT_DOWNLOADS = 2
DEFAULT_MAX_DELAY_SECONDS = 3
NATIVE_TMPDIRS = ["TEMP", "TMP", "TMPDIR"]
STOPWORDS_FALLBACK = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren', 'as',
    'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'cannot',
    'could', 'couldn', 'did', 'didn', 'do', 'does', 'doesn', 'doing', 'don', 'down', 'during', 'each', 'few',
    'for', 'from', 'further', 'had', 'hadn', 'has', 'hasn', 'have', 'haven', 'having', 'he', 'her', 'here',
    'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'isn', 'it', 'its',
    'itself', 'just', 'll', 'me', 'more', 'most', 'mustn', 'my', 'myself', 'needn', 'no', 'nor', 'not', 'now',
    'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 're',
    's', 'same', 'shan', 'she', 'should', 'shouldn', 'so', 'some', 'such', 't', 'than', 'that', 'the', 'their',
    'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too',
    'under', 'until', 'up', 've', 'very', 'was', 'wasn', 'we', 'were', 'weren', 'what', 'when', 'where', 'which',
    'while', 'who', 'whom', 'why', 'will', 'with', 'won', 'would', 'wouldn', 'you', 'your', 'yours', 'yourself',
    'yourselves'
}


def get_temp_directory() -> Path:
    for var in NATIVE_TMPDIRS:
        value = os.environ.get(var)
        if value:
            return Path(value)
    return Path('/tmp')


def supports_ansi() -> bool:
    return bool(os.environ.get('TERM', '') and os.environ.get('TERM') != 'dumb')


def print_info(message: str) -> None:
    print(message)


def print_warning(message: str) -> None:
    if supports_ansi():
        print(f"\033[33mWARNING:\033[0m {message}")
    else:
        print(f"WARNING: {message}")


def print_error(message: str) -> None:
    if supports_ansi():
        print(f"\033[31mERROR:\033[0m {message}")
    else:
        print(f"ERROR: {message}")


def run_git_command(root: Path, args: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(['git', '-C', str(root)] + args, capture_output=True, text=True)


def ensure_git_repo(root: Path) -> None:
    result = run_git_command(root, ['rev-parse', '--is-inside-work-tree'])
    if result.returncode != 0 or result.stdout.strip() != 'true':
        raise SystemExit(f"Directory {root} is not a Git repository.")


def git_grep_files(root: Path, pattern: str) -> List[Path]:
    result = run_git_command(root, ['grep', '-l', '--', pattern, '--', '*.md'])
    if result.returncode not in (0, 1):
        raise SystemExit(f"git grep failed: {result.stderr.strip()}")
    return [Path(root / line.strip()) for line in result.stdout.splitlines() if line.strip()]


def git_grep_permalink(root: Path, permalink: str) -> Optional[Path]:
    escaped_permalink = re.escape(permalink)
    pattern = f"^permalink:\\s*['\"]?{escaped_permalink}['\"]?\\s*$"
    
    result = run_git_command(root, ['grep', '-n', '-E', '--', pattern, '--', '*.md'])
    if result.returncode == 0 and result.stdout:
        first_line = result.stdout.splitlines()[0]
        path_part = first_line.split(':', 1)[0]
        return Path(root / path_part)
    return None


def parse_yaml_front_matter(md_path: Path) -> Dict[str, object]:
    metadata: Dict[str, object] = {}
    if not md_path.exists():
        return metadata
    with md_path.open('r', encoding='utf-8') as fh:
        lines = fh.readlines()
    if not lines or lines[0].strip() != '---':
        return metadata
    current_key: Optional[str] = None
    for line in lines[1:]:
        stripped = line.rstrip('\n')
        if stripped.strip() == '---':
            break
        if stripped.lstrip().startswith('-') and current_key == 'tags':
            current_value = stripped.lstrip()[1:].strip()
            current_value = current_value.strip("'\"")
            if current_value:
                metadata.setdefault('tags', [])
                metadata['tags'].append(current_value)
            continue
        if ':' not in stripped:
            continue
        key, _, value = stripped.partition(':')
        key = key.strip()
        value = value.strip().strip("'\"")
        if key == 'tags':
            metadata['tags'] = []
            current_key = 'tags'
        else:
            metadata[key] = value
            current_key = None
    return metadata


def get_tag_list(value: object) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [part.strip() for part in value.split(',') if part.strip()]
    return []


def get_stopwords() -> set:
    try:
        import nltk
        from nltk.corpus import stopwords
        try:
            return set(stopwords.words('english'))
        except LookupError:
            nltk.download('stopwords', quiet=True)
            return set(stopwords.words('english'))
    except Exception:
        return STOPWORDS_FALLBACK


STOPWORDS = get_stopwords()


def slugify_title(title: str) -> str:
    title = html.unescape(title or '')
    tokens = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", title)
    words = [token for token in tokens if token.isalpha()]
    meaningful = [w for w in words if w.lower() not in STOPWORDS]
    if len(meaningful) >= 3:
        chosen = meaningful[-3:]
    else:
        chosen = meaningful
        if len(chosen) < 3:
            remainder = [w for w in words if w not in chosen]
            chosen += remainder[:3 - len(chosen)]
    if not chosen:
        chosen = [w for w in words][:3] or ['Episode']
    cleaned = [re.sub(r'[^A-Za-z]', '', word).title() for word in chosen if word]
    cleaned = [word for word in cleaned if word]
    if not cleaned:
        cleaned = ['Episode']
    return ' '.join(cleaned[:3])


def safe_yaml_value(value: Optional[str], force_unquoted: bool = False) -> str:
    if value is None:
        return ''
    text = str(value).strip()
    if text == '':
        return ''
    if force_unquoted:
        return text
    if re.search(r'[:\n\r]|^\s|\s$|["\'{}\[\],&*#?\-<>=!%@`]', text):
        text = text.replace('"', '\\"')
        return f'"{text}"'
    return text


def make_tag_lines(tag_csv: Optional[str]) -> List[str]:
    if not tag_csv:
        return []
    return [part.strip() for part in tag_csv.split(',') if part.strip()]


def format_duration(duration_text: Optional[str]) -> str:
    if not duration_text:
        return ''
    cleaned = duration_text.strip()
    if cleaned.isdigit():
        total_seconds = int(cleaned)
    elif ':' in cleaned:
        parts = [p.strip() for p in cleaned.split(':') if p.strip().isdigit()]
        try:
            parts = list(map(int, parts))
        except ValueError:
            total_seconds = 0
        else:
            if len(parts) == 1:
                total_seconds = parts[0]
            elif len(parts) == 2:
                total_seconds = parts[0] * 60 + parts[1]
            else:
                total_seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
    else:
        try:
            total_seconds = int(float(cleaned))
        except Exception:
            total_seconds = 0

    if total_seconds < 0:
        total_seconds = 0

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def parse_author(author_text: Optional[str]) -> str:
    if not author_text:
        return ''
    author_text = author_text.strip()
    if '|' in author_text:
        parts = [p.strip() for p in author_text.split('|') if p.strip()]
        if len(parts) > 1:
            return parts[-1]
    return author_text


def abbreviate_channel(channel_title: Optional[str]) -> str:
    if not channel_title:
        return ''
    words = re.findall(r"[A-Za-z0-9]+", channel_title)
    if not words:
        return ''
    return ''.join(word[0].upper() for word in words)[:4]


def platform_from_url(url: str) -> str:
    if not url:
        return ''
    host = urlparse(url).hostname or ''
    host = host.lower()
    if host.startswith('www.'):
        host = host[4:]
    if host.endswith('.com'):
        host = host[:-4]
    return host.title()


def basename_from_url(url: str) -> str:
    if not url:
        return ''
    parsed = urlparse(url)
    return Path(parsed.path).name


def parse_rss_feed(xml_text: str) -> Tuple[str, List[Dict[str, str]]]:
    import xml.etree.ElementTree as ET

    ns = {
        'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
        'podcast': 'https://podcastindex.org/namespace/1.0',
        'content': 'http://purl.org/rss/1.0/modules/content/'
    }
    root = ET.fromstring(xml_text)
    channel = root.find('channel') or root.find('./rss/channel')
    if channel is None:
        channel = root.find('.//channel')
    channel_title = ''
    if channel is not None:
        title_elem = channel.find('title')
        if title_elem is not None and title_elem.text:
            channel_title = title_elem.text.strip()

    items: List[Dict[str, str]] = []
    for item in root.findall('.//item'):
        title = (item.find('title').text or '').strip() if item.find('title') is not None else ''
        link = (item.find('link').text or '').strip() if item.find('link') is not None else ''
        pub_date = (item.find('pubDate').text or '').strip() if item.find('pubDate') is not None else ''
        description = ''
        desc_elem = item.find('description')
        if desc_elem is not None and desc_elem.text:
            description = desc_elem.text
        else:
            summary_elem = item.find('itunes:summary', ns)
            if summary_elem is not None and summary_elem.text:
                description = summary_elem.text
        duration_value = ''
        duration_elem = item.find('itunes:duration', ns)
        if duration_elem is not None and duration_elem.text:
            duration_value = duration_elem.text.strip()
        keywords = ''
        keywords_elem = item.find('itunes:keywords', ns)
        if keywords_elem is not None and keywords_elem.text:
            keywords = keywords_elem.text.strip()
        author = ''
        author_elem = item.find('itunes:author', ns)
        if author_elem is not None and author_elem.text:
            author = author_elem.text.strip()
        enclosure_url = ''
        enclosure_elem = item.find('enclosure')
        if enclosure_elem is not None:
            enclosure_url = enclosure_elem.attrib.get('url', '').strip()
        transcript_url = ''
        transcript_type = ''
        transcript_elem = item.find('podcast:transcript', ns)
        if transcript_elem is not None:
            transcript_url = transcript_elem.attrib.get('url', '').strip()
            transcript_type = transcript_elem.attrib.get('type', '').strip().lower()
        if transcript_url and transcript_type not in ('text/plain', 'text/vtt'):
            transcript_url = ''
            transcript_type = ''
        items.append({
            'title': title,
            'link': link,
            'pubDate': pub_date,
            'description': description,
            'itunes_duration': duration_value,
            'itunes_keywords': keywords,
            'itunes_author': author,
            'enclosure_url': enclosure_url,
            'transcript_url': transcript_url,
            'transcript_type': transcript_type,
        })
    return channel_title, items


def html_to_markdown(html_text: str) -> str:
    if not html_text:
        return ''
    text = html.unescape(html_text).strip()
    text = re.sub(r'(?is)<table.*?</table>', ' ', text)
    text = re.sub(r'(?is)<(pre|code).*?</\1>', ' ', text)
    text = re.sub(r'(?i)<br\s*/?>', '\n', text)
    text = re.sub(r'(?i)</p>', '\n\n', text)
    text = re.sub(r'(?i)<p[^>]*>', '', text)
    for level in range(1, 4):
        text = re.sub(rf'(?i)<h{level}[^>]*>', '\n' + ('#' * level) + ' ', text)
        text = re.sub(rf'(?i)</h{level}>', '\n\n', text)
    text = re.sub(r'(?i)<ul[^>]*>', '\n', text)
    text = re.sub(r'(?i)</ul>', '\n', text)
    text = re.sub(r'(?i)<ol[^>]*>', '\n', text)
    text = re.sub(r'(?i)</ol>', '\n', text)
    text = re.sub(r'(?i)<li[^>]*>', '\n- ', text)
    text = re.sub(r'(?i)</li>', '', text)
    text = re.sub(r'(?i)<strong[^>]*>', '**', text)
    text = re.sub(r'(?i)</strong>', '**', text)
    text = re.sub(r'(?i)<b[^>]*>', '**', text)
    text = re.sub(r'(?i)</b>', '**', text)
    text = re.sub(r'(?i)<em[^>]*>', '_', text)
    text = re.sub(r'(?i)</em>', '_', text)
    text = re.sub(r'(?i)<i[^>]*>', '_', text)
    text = re.sub(r'(?i)</i>', '_', text)

    def anchor_replace(match: re.Match) -> str:
        href = match.group(1) or ''
        text_inner = match.group(2) or ''
        text_inner = text_inner.strip()
        if href and text_inner and href.strip() == text_inner.strip():
            return text_inner
        if href and not text_inner:
            return href
        if href and text_inner.lower() in {'link', 'click here', 'here'}:
            return f'[{href}]({href})'
        if href and text_inner:
            return f'[{text_inner}]({href})'
        return text_inner

    text = re.sub(r'(?is)<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', anchor_replace, text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def format_date(pub_date: str) -> Tuple[str, str]:
    if not pub_date:
        now = datetime.utcnow()
        return now.strftime('%Y-%m-%d'), now.strftime('%Y%m%d%H%M%S')
    try:
        dt = parsedate_to_datetime(pub_date)
    except Exception:
        try:
            dt = datetime.strptime(pub_date.strip(), '%a, %d %b %Y %H:%M:%S %z')
        except Exception:
            dt = datetime.utcnow()
    if dt.tzinfo is not None:
        dt = dt.astimezone(tz=None)
    return dt.strftime('%Y-%m-%d'), dt.strftime('%Y%m%d%H%M%S')


def build_front_matter(rss_item: Dict[str, str], channel_title: str) -> Tuple[str, Dict[str, object]]:
    published_date, pubkey = format_date(rss_item.get('pubDate', ''))
    return pubkey, {
        'tags': make_tag_lines(rss_item.get('itunes_keywords', '')),
        'author': parse_author(rss_item.get('itunes_author', '')),
        'date': published_date,
        'created': '',
        'published': '',
        'updated': '',
        'type': 'Podcast',
        'channel': abbreviate_channel(channel_title),
        'catalog': '',
        'platform': platform_from_url(rss_item.get('link', '')),
        'episode': '',
        'duration': format_duration(rss_item.get('itunes_duration', '')),
        'permalink': rss_item.get('link', ''),
        'download': rss_item.get('enclosure_url', ''),
        'transcript': rss_item.get('transcript_url', ''),
        'title': rss_item.get('title', ''),
    }


def render_yaml(front: Dict[str, object]) -> str:
    tags = get_tag_list(front.get('tags', []))
    lines: List[str] = ['tags:']
    for tag in tags:
        # Enforce unquoted structure for all simple tag metadata values
        lines.append(f'  - {safe_yaml_value(tag, force_unquoted=True)}')
    lines.append(f'author: {safe_yaml_value(str(front.get("author", "")))}')
    
    lines.append(f'date: {safe_yaml_value(str(front.get("date", "")), force_unquoted=True)}')
    lines.append(f'created: {safe_yaml_value(str(front.get("created", "")))}')
    lines.append(f'published: {safe_yaml_value(str(front.get("published", "")))}')
    lines.append(f'updated: {safe_yaml_value(str(front.get("updated", "")))}')
    lines.append('')
    lines.append(f'type: {safe_yaml_value(str(front.get("type", "")))}')
    lines.append(f'channel: {safe_yaml_value(str(front.get("channel", "")))}')
    lines.append(f'catalog: {safe_yaml_value(str(front.get("catalog", "")))}')
    lines.append(f'platform: {safe_yaml_value(str(front.get("platform", "")))}')
    lines.append(f'episode: {safe_yaml_value(str(front.get("episode", "")))}')
    lines.append(f'duration: {safe_yaml_value(str(front.get("duration", "")), force_unquoted=True)}')
    lines.append(f'permalink: {safe_yaml_value(str(front.get("permalink", "")), force_unquoted=True)}')
    lines.append(f'download: {safe_yaml_value(str(front.get("download", "")), force_unquoted=True)}')
    
    lines.append(f'title: {safe_yaml_value(str(front.get("title", "")).title(), force_unquoted=True)}')
    
    if str(front.get('transcript', '')).strip():
        lines.append(f'transcript: {safe_yaml_value(str(front.get("transcript", "")))}')
    return '\n'.join(lines)


def build_markdown_content(rss_item: Dict[str, str], front: Dict[str, object]) -> str:
    title = rss_item.get('title', '')
    platform = str(front.get('platform', ''))
    filename = basename_from_url(rss_item.get('enclosure_url', ''))
    description = html_to_markdown(rss_item.get('description', ''))
    tags_line = ', '.join(make_tag_lines(rss_item.get('itunes_keywords', '')))
    lines = [
        '---',
        render_yaml(front),
        '---',
        '',
        f'# {title}',
        '',
        '## Podcast',
        '',
        f'{title}',
        '',
        f'{platform}, {filename} -->',
        '',
        description,
        ''
    ]
    transcript_url = str(front.get('transcript', '')).strip()
    if transcript_url:
        transcript_name = basename_from_url(transcript_url)
        lines += [
            '## Related',
            '',
            f'- Transcript [[{transcript_name}]]',
            ''
        ]
    lines.append(f'- Tags = {tags_line}')
    lines.append('')
    return '\n'.join(lines)


def download_url(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    curl_path = shutil.which('curl')
    if curl_path:
        result = subprocess.run([curl_path, '-fsSL', url, '-o', str(output_path)], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"curl failed: {result.stderr.strip()}")
        return
    with urlopen(url) as response, output_path.open('wb') as out_fh:
        out_fh.write(response.read())


def threaded_download(url: str, output_path: Path, active: List[threading.Thread], lock: threading.Lock) -> None:
    try:
        download_url(url, output_path)
        print_info(f"Downloaded transcript to {output_path}")
    except Exception as exc:
        print_warning(f"Transcript download failed for {url}: {exc}")
    finally:
        with lock:
            current = threading.current_thread()
            if current in active:
                active.remove(current)


def enqueue_download(url: str, output_path: Path, active: List[threading.Thread], lock: threading.Lock, max_workers: int) -> None:
    while True:
        with lock:
            if len(active) < max_workers:
                break
        time.sleep(0.2)
    delay = random.uniform(0, DEFAULT_MAX_DELAY_SECONDS)
    time.sleep(delay)
    thread = threading.Thread(target=threaded_download, args=(url, output_path, active, lock), daemon=True)
    with lock:
        active.append(thread)
    thread.start()


def find_output_directory(root: Path) -> Path:
    pages_dir = root / 'pages'
    assets_dir = root / 'assets'
    if pages_dir.exists() and pages_dir.is_dir():
        return pages_dir
    if assets_dir.exists() and assets_dir.is_dir():
        print_warning('`pages/` folder not found, using repository root for sidecars because `assets/` exists.')
        return root
    raise SystemExit('Could not locate `pages/` directory or `assets/` in repository root.')


def extract_title_from_markdown(path: Path) -> str:
    content = path.read_text(encoding='utf-8')
    if not content.strip():
        return ''
    parts = content.split('---', 2)
    body = parts[-1] if len(parts) >= 3 else content
    match = re.search(r'^#\s+(.*)', body, re.MULTILINE)
    return match.group(1).strip() if match else ''


def gather_existing_sidecars(root: Path) -> List[Tuple[Path, Dict[str, object]]]:
    candidates = git_grep_files(root, 'type: Podcast')
    results: List[Tuple[Path, Dict[str, object]]] = []
    for path in candidates:
        if 'Template' in str(path):
            continue
        metadata = parse_yaml_front_matter(path)
        if str(metadata.get('type', '')).strip().lower() == 'podcast':
            results.append((path, metadata))
    return results


def truncate_for_report(text: str, width: int = 60) -> str:
    if len(text) <= width:
        return text
    return text[:width - 3] + '...'


def report_sidecars(root: Path) -> None:
    ensure_git_repo(root)
    sidecars = gather_existing_sidecars(root)
    if not sidecars:
        print_info('No podcast sidecar markdown files found.')
        return
    print_info('filename,date,title,permalink')
    for path, metadata in sidecars:
        filename = str(path)
        date = str(metadata.get('date', '')).strip()
        title = str(metadata.get('title', '') or '').strip() or extract_title_from_markdown(path)
        permalink = str(metadata.get('permalink', '')).strip()
        title_escaped = title.replace('"', '""')
        print_info(f'{filename},{date},"{title_escaped}",{permalink}')


def build_update_plan(existing_metadata: Dict[str, object], rss_front: Dict[str, object]) -> Tuple[Dict[str, object], List[str]]:
    updated = existing_metadata.copy()
    changes: List[str] = []
    for key in ['author', 'date', 'platform', 'duration', 'download', 'permalink', 'transcript', 'title']:
        rss_value = str(rss_front.get(key, '')).strip()
        existing_value = str(existing_metadata.get(key, '')).strip()
        
        if key == 'title':
            rss_value = rss_value.title()
            
        if existing_value == '' and rss_value:
            updated[key] = rss_value
            changes.append(key)
    existing_tags = get_tag_list(existing_metadata.get('tags', []))
    rss_tags = get_tag_list(rss_front.get('tags', []))
    if not existing_tags and rss_tags:
        updated['tags'] = rss_tags
        changes.append('tags')
    return updated, changes


def detect_conflicts(existing_metadata: Dict[str, object], rss_front: Dict[str, object]) -> List[str]:
    conflicts: List[str] = []
    for key in ['author', 'date', 'platform', 'duration', 'download', 'permalink', 'transcript', 'title']:
        rss_value = str(rss_front.get(key, '')).strip()
        existing_value = str(existing_metadata.get(key, '')).strip()
        
        if key == 'title':
            rss_value = rss_value.title()
            
        if existing_value and rss_value and existing_value != rss_value:
            conflicts.append(f"{key}: existing='{existing_value}' rss='{rss_value}'")
        elif not existing_value and rss_value:
            conflicts.append(f"{key}: missing in markdown, rss has value")
    existing_tags = get_tag_list(existing_metadata.get('tags', []))
    rss_tags = get_tag_list(rss_front.get('tags', []))
    if rss_tags and set(existing_tags) != set(rss_tags):
        conflicts.append(f"tags: existing={existing_tags} rss={rss_tags}")
    if str(existing_metadata.get('type', '')).strip().lower() != 'podcast':
        conflicts.append('type: not Podcast')
    return conflicts


def update_markdown_sidecar(path: Path, rss_front: Dict[str, object], dry_run: bool) -> bool:
    metadata = parse_yaml_front_matter(path)
    updated_metadata, changes = build_update_plan(metadata, rss_front)
    if not changes:
        return False
    if dry_run:
        print_info(f'[DRY-RUN] Would update {path}: {", ".join(changes)}')
        return True
    content = path.read_text(encoding='utf-8')
    first = content.find('---')
    second = content.find('---', first + 3)
    if first == -1 or second == -1:
        print_warning(f'Could not parse front matter for {path}')
        return False
    body = content[second + 3:].lstrip('\n')
    path.write_text('---\n' + render_yaml(updated_metadata) + '\n---\n\n' + body, encoding='utf-8')
    print_info(f'Updated {path} ({len(changes)} fields)')
    return True


def generate_sidecar_filename(pubkey: str, title_phrase: str) -> str:
    safe_phrase = re.sub(r'[^A-Za-z ]+', '', title_phrase).strip()
    safe_phrase = re.sub(r'\s+', ' ', safe_phrase)
    if not safe_phrase:
        safe_phrase = 'Episode'
    return f"{pubkey} {safe_phrase}.md"


def create_sidecar_file(output_dir: Path, rss_item: Dict[str, str], channel_title: str, dry_run: bool) -> Path:
    pubkey, front = build_front_matter(rss_item, channel_title)
    title_phrase = slugify_title(rss_item.get('title', ''))
    filename = generate_sidecar_filename(pubkey, title_phrase)
    path = output_dir / filename
    count = 1
    while path.exists():
        path = output_dir / f"{pubkey} {title_phrase} {count}.md"
        count += 1
    if dry_run:
        print_info(f'[DRY-RUN] Would create {path}')
        return path
    content = build_markdown_content(rss_item, front)
    path.write_text(content, encoding='utf-8')
    print_info(str(path))
    return path


def create_transcript_downloads(tasks: List[Tuple[str, Path]], dry_run: bool) -> None:
    if dry_run or not tasks:
        return
    active: List[threading.Thread] = []
    lock = threading.Lock()
    for url, out_path in tasks:
        enqueue_download(url, out_path, active, lock, DEFAULT_CONCURRENT_DOWNLOADS)
    for thread in list(active):
        thread.join()


def main() -> None:
    parser = argparse.ArgumentParser(description='Create and inspect podcast RSS markdown sidecars')
    parser.add_argument('--directory', type=Path, help='Repository root for markdown vault')
    parser.add_argument('--rss-feed', help='RSS feed URL to process')
    parser.add_argument('--limit', type=int, help='Limit new sidecars to create')
    parser.add_argument('--dry-run', action='store_true', help='Do not modify files')
    parser.add_argument('--report', action='store_true', help='Report existing podcast sidecars')
    parser.add_argument('--update', action='store_true', help='Update missing YAML front matter from RSS feed')
    parser.add_argument('--check-yaml', action='store_true', help='Dry-run conflict check between RSS and sidecar YAML')
    args = parser.parse_args()
    
    root = (args.directory or Path.cwd()).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f'Directory {root} does not exist.')
    ensure_git_repo(root)
    
    if args.report:
        report_sidecars(root)
        if not args.rss_feed:
            return
            
    if args.check_yaml and not args.rss_feed:
        raise SystemExit('--check-yaml requires --rss-feed')
    if args.update and not args.rss_feed:
        raise SystemExit('--update requires --rss-feed')
        
    if args.rss_feed:
        rss_result = subprocess.run(['curl', '-fsSL', args.rss_feed], capture_output=True, text=True)
        if rss_result.returncode != 0:
            raise SystemExit(f'Failed to download RSS feed: {rss_result.stderr.strip()}')
        channel_title, rss_items = parse_rss_feed(rss_result.stdout)
        if not rss_items:
            print_info('No items found in RSS feed.')
            return
            
        if args.check_yaml:
            print_info('Checking YAML conflicts...')
            conflicts_found = 0
            for rss_item in rss_items:
                path = git_grep_permalink(root, rss_item['link'])
                if not path:
                    continue
                _, front = build_front_matter(rss_item, channel_title)
                existing = parse_yaml_front_matter(path)
                conflicts = detect_conflicts(existing, front)
                if conflicts:
                    conflicts_found += 1
                    print_info(f'{path}:')
                    for conflict in conflicts:
                        print_info(f'  - {conflict}')
            if conflicts_found == 0:
                print_info('No YAML conflicts detected.')
            return
            
        if args.update:
            print_info('Updating existing sidecars...')
            updated_count = 0
            for rss_item in rss_items:
                path = git_grep_permalink(root, rss_item['link'])
                if not path:
                    continue
                _, front = build_front_matter(rss_item, channel_title)
                if update_markdown_sidecar(path, front, args.dry_run):
                    updated_count += 1
            print_info(f'Processed {len(rss_items)} RSS items, updated {updated_count} files.')
            return
            
        output_dir = find_output_directory(root)
        assets_dir = output_dir / 'assets'
        if not args.dry_run:
            assets_dir.mkdir(parents=True, exist_ok=True)
            
        created = 0
        download_tasks: List[Tuple[str, Path]] = []
        
        # In-memory registries to prevent identical items in the same batch from colliding
        seen_permalinks = set()
        seen_transcripts = set()
        
        for rss_item in rss_items:
            if args.limit is not None and created >= args.limit:
                break
                
            permalink = rss_item.get('link', '').strip()
            if not permalink:
                continue
                
            # Skip if we already touched it in this run, or if it's already saved to Git
            if permalink in seen_permalinks or git_grep_permalink(root, permalink):
                continue
                
            seen_permalinks.add(permalink)
            print_info(f'Processing episode: {rss_item.get("title", "<no title>")}')
            
            transcript_url = rss_item.get('transcript_url', '').strip()
            if transcript_url and transcript_url not in seen_transcripts:
                seen_transcripts.add(transcript_url)
                download_tasks.append((transcript_url, assets_dir / basename_from_url(transcript_url)))
                
            create_sidecar_file(output_dir, rss_item, channel_title, args.dry_run)
            created += 1
            
        create_transcript_downloads(download_tasks, args.dry_run)
        print_info(f'Processed {len(rss_items)} RSS items, created {created} new sidecars.')
		
if __name__ == '__main__':
    main()