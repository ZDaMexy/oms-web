"""Snapshot every table listed by Zris; retain only chart browsing metadata."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
from http.client import HTTPException
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

INDEX = 'https://zris.work/bmstable.htm'
ORIGIN_DATA = {'https://iidxtool.kasacontent.com/homage/json/data.json'}
ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / 'resources/oms/difficulty-tables'


def mirror_url(url):
    parts = urlsplit(url)
    if parts.hostname != 'zris.work' or not parts.path.startswith('/bmstable/') or parts.username or parts.password or parts.port:
        raise ValueError('Table metadata must stay within the listed Zris mirror')
    return urlunsplit(('https', 'zris.work', parts.path, parts.query, ''))


class IndexParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables, self.cells, self.cell = [], [], None
        self.anchor = None
        self.in_table = False
        self.group, self.remaining = '', 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'table':
            self.in_table = True
        elif tag == 'tr':
            self.cells = []
        elif tag == 'td':
            self.cell = {'text': [], 'links': [], 'rowspan': int(attrs.get('rowspan', '1'))}
        elif tag == 'a' and 'href' in attrs:
            self.anchor = {'url': attrs['href'], 'text': []}

    def handle_data(self, text):
        if self.cell is not None:
            self.cell['text'].append(text)
        if self.anchor is not None:
            self.anchor['text'].append(text)

    def handle_endtag(self, tag):
        if tag == 'a' and self.anchor is not None:
            link = self.anchor
            link['name'] = ' '.join(''.join(link.pop('text')).split())
            self.anchor = None
            if self.cell is not None:
                self.cell['links'].append(link)
            elif not self.in_table and urlsplit(link['url']).hostname == 'zris.work' and urlsplit(link['url']).path.startswith('/bmstable/'):
                self.tables.append({'name': link['name'], 'url': mirror_url(link['url']), 'source_url': mirror_url(link['url'])})
        elif tag == 'td' and self.cell is not None:
            self.cell['text'] = ' '.join(''.join(self.cell['text']).split())
            self.cells.append(self.cell)
            self.cell = None
        elif tag == 'tr' and self.cells:
            if self.remaining:
                group = self.group
                self.remaining -= 1
            else:
                group = ''
            if self.cells[0]['rowspan'] > 1:
                group = self.group = self.cells[0]['text']
                self.remaining = self.cells[0]['rowspan'] - 1
            for cell in self.cells:
                for link in cell['links']:
                    parts = urlsplit(link['url'])
                    if parts.hostname == 'zris.work' and parts.path.startswith('/bmstable/'):
                        origins = self.cells[-1]['links']
                        self.tables.append({'name': (group + ' · ' if group else '') + link['name'], 'url': mirror_url(link['url']), 'source_url': origins[-1]['url'] if origins else None})
        elif tag == 'table':
            self.in_table = False


class HeaderParser(HTMLParser):
    url = None

    def handle_starttag(self, tag, attrs):
        attrs = {key.lower(): value for key, value in attrs}
        if tag == 'meta' and (attrs.get('name') or '').lower() == 'bmstable':
            self.url = attrs.get('content')


def title_key(title):
    return unicodedata.normalize('NFKC', title or '').strip().casefold()


def initial(title):
    first = title_key(title)[:1].upper()
    if len(first) == 1 and 'A' <= first <= 'Z':
        return first
    return '0-9' if first and first in '0123456789' else '#'


def chart_key(item):
    letter = item['initial']
    return (0 if letter == '0-9' else 2 if letter == '#' else 1, title_key(item['title']), item['md5'] or '', item['row'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--index-file', type=Path)
    parser.add_argument('--reuse-reads', action='store_true')
    args = parser.parse_args()
    args.evidence.mkdir(parents=True, exist_ok=True)
    raw = args.evidence / 'raw'
    raw.mkdir(exist_ok=True)
    reads = []

    def fetch(url, name, limit=32 * 1024 * 1024):
        saved = raw / name
        if args.reuse_reads and saved.exists():
            data = saved.read_bytes()
            if len(data) > limit:
                raise ValueError('Retained response exceeds metadata limit')
            reads.append({'url': url, 'file': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'retained': True})
            return data
        request = Request(url, headers={'Accept': '*/*'})
        started = time.monotonic()
        with urlopen(request, timeout=25) as response:
            if urlsplit(response.url).hostname not in ('zris.work', 'iidxtool.kasacontent.com'):
                raise ValueError('Unexpected mirror redirect')
            chunks, size = [], 0
            while chunk := response.read(65536):
                size += len(chunk)
                if size > limit:
                    raise ValueError('Mirror response exceeds metadata limit')
                if time.monotonic() - started > 90:
                    raise TimeoutError('Metadata read exceeded 90 seconds')
                chunks.append(chunk)
            data = b''.join(chunks)
        (raw / name).write_bytes(data)
        reads.append({'url': url, 'file': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
        return data

    index = args.index_file.read_bytes() if args.index_file else fetch(INDEX, 'index.html', 512 * 1024)
    index_parser = IndexParser()
    index_parser.feed(index.decode('utf-8-sig'))
    tables = index_parser.tables
    if not 1 <= len(tables) <= 200 or len({row['url'] for row in tables}) != len(tables):
        raise ValueError('Missing or duplicated listed tables')
    for table in tables:
        if table['source_url'] is not None:
            origin = urlsplit(table['source_url'])
            if origin.scheme not in ('http', 'https') or not origin.hostname or origin.username or origin.password:
                raise ValueError('Unexpected original table link')
        path = Path(urlsplit(table['url']).path)
        table['id'] = path.stem if path.suffix in ('.htm', '.html') else path.parent.name
        if not re.fullmatch('[a-z0-9_-]+', table['id']):
            raise ValueError('Unexpected table ID')
    if len({row['id'] for row in tables}) != len(tables):
        raise ValueError('Duplicated table IDs')
    OUTPUT.mkdir(parents=True, exist_ok=True)

    def load(table):
        table = dict(table)
        table_id = table['id']
        try:
            header_url = table['url']
            if Path(urlsplit(header_url).path).suffix in ('.htm', '.html'):
                html = fetch(header_url, table_id + '-page.html', 512 * 1024)
                html_parser = HeaderParser()
                html_parser.feed(html.decode('utf-8-sig'))
                if not html_parser.url:
                    raise ValueError('Listed page has no bmstable header')
                header_url = mirror_url(urljoin(header_url, html_parser.url))
            header_bytes = fetch(header_url, table_id + '-header.json', 2 * 1024 * 1024)
            header = json.loads(header_bytes.decode('utf-8-sig'))
            data_url = urljoin(header_url, header['data_url'])
            if data_url not in ORIGIN_DATA:
                data_url = mirror_url(data_url)
            data_bytes = fetch(data_url, table_id + '-data.json')
            rows = json.loads(data_bytes.decode('utf-8-sig'))
            if not isinstance(rows, list) or len(rows) > 200000:
                raise ValueError('Unexpected chart list')
            items = []
            excluded_headers = 0
            for number, row in enumerate(rows):
                if not isinstance(row, dict):
                    raise ValueError('Unexpected chart row')
                if row.get('md5') == 'md5' and row.get('title') == 'title subtitle':
                    excluded_headers += 1
                    continue
                source_id = row.get('md5') or None
                md5 = source_id.lower() if isinstance(source_id, str) and re.fullmatch('[0-9a-fA-F]{32}', source_id) else None
                values = {key: row.get(key) or None for key in ('title', 'artist')}
                if any(value is not None and (not isinstance(value, str) or len(value) > 2000) for value in values.values()):
                    raise ValueError('Unexpected title or artist')
                level = row.get('level')
                if level is not None and not isinstance(level, (str, int, float)):
                    raise ValueError('Unexpected chart level')
                items.append({'row': number, 'md5': md5, **values, 'level': str(level) if level is not None else None, 'initial': initial(values['title'])})
            items.sort(key=chart_key)
            table.update({'header_url': header_url, 'data_url': data_url, 'symbol': str(header.get('symbol') or ''), 'count': len(items), 'unlinked_count': sum(item['md5'] is None for item in items), 'excluded_header_rows': excluded_headers, 'status': 'ok', 'header_sha256': hashlib.sha256(header_bytes).hexdigest(), 'data_sha256': hashlib.sha256(data_bytes).hexdigest()})
            payload = {'id': table_id, 'items': items}
            (OUTPUT / (table_id + '.json')).write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
            print(table_id + ': ' + str(len(items)) + ' rows', flush=True)
        except (HTTPError, URLError, TimeoutError, HTTPException, ValueError, KeyError) as error:
            table.update({'status': 'unavailable', 'count': None, 'error': str(error)})
            print(table_id + ': unavailable: ' + str(error), flush=True)
        return table

    with ThreadPoolExecutor(max_workers=2) as pool:
        tables = list(pool.map(load, tables))
    manifest = {'index_url': INDEX, 'fetched_at': datetime.now(timezone.utc).isoformat(), 'index_sha256': hashlib.sha256(index).hexdigest(), 'tables': tables}
    (OUTPUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (args.evidence / 'source-reads.json').write_text(json.dumps({'index_sha256': manifest['index_sha256'], 'reads': reads, 'tables': tables}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'listed': len(tables), 'available': sum(table['status'] == 'ok' for table in tables), 'rows': sum(table['count'] or 0 for table in tables)}))


if __name__ == '__main__':
    main()
