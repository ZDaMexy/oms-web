# Licensed under AGPL-3.0-or-later; see LICENCE.
"""Measure a fresh local process's homepage and declared assets; not a browser waterfall."""
import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.parse import urljoin, urlsplit

import httpx


BASE = 'http://127.0.0.1:8090'
ROOT = Path(__file__).resolve().parents[1]


class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()

    def handle_starttag(self, tag, attributes):
        values = dict(attributes)
        if tag in ('script', 'img') and values.get('src'):
            self.urls.add(urljoin(BASE, values['src']))
        if tag == 'link' and values.get('rel') in ('stylesheet', 'icon') and values.get('href'):
            self.urls.add(urljoin(BASE, values['href']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9-]{1,40}', args.tag):
        raise ValueError('Use a plain evidence tag')
    output = ROOT / ('artifacts/assets-' + args.tag + '.json')
    if output.exists():
        raise FileExistsError('Keep earlier measurement evidence')
    requests = []
    with httpx.Client(base_url=BASE, trust_env=False, timeout=35) as client:
        first = None
        for ordinal in range(2):
            began = time.monotonic()
            response = client.get('/')
            response.raise_for_status()
            requests.append({'path': '/', 'kind': 'first-probe' if ordinal == 0 else 'immediate-warm',
                             'ms': round((time.monotonic() - began) * 1000, 3),
                             'decoded_bytes': len(response.content),
                             'cache_control': response.headers.get('cache-control')})
            if ordinal == 0:
                first = response.text
        assets = Assets()
        assets.feed(first)
        for url in sorted(assets.urls):
            if urlsplit(url).netloc != urlsplit(BASE).netloc:
                raise ValueError('The homepage declares an unexpected remote resource')
            began = time.monotonic()
            with client.stream('GET', url, headers={'Accept-Encoding': 'gzip'}) as response:
                response.raise_for_status()
                data = b''.join(response.iter_raw())
                requests.append({'path': urlsplit(url).path, 'kind': 'declared-asset',
                                 'ms': round((time.monotonic() - began) * 1000, 3),
                                 'received_entity_bytes': len(data),
                                 'content_encoding': response.headers.get('content-encoding', 'identity'),
                                 'cache_control': response.headers.get('cache-control')})
    manifest = json.loads((ROOT / 'public/assets/manifest.json').read_text())
    sizes = []
    for asset in sorted(set(manifest.values())):
        if not isinstance(asset, str) or not asset.startswith('/assets/') or '..' in asset.split('/'):
            raise ValueError('Unexpected generated asset path')
        filename = ROOT / ('public' + asset)
        if not filename.is_file() or filename.is_symlink():
            raise ValueError('The built asset is absent')
        sizes.append({'path': asset, 'bytes': filename.stat().st_size})
    report = {'completed_at': datetime.now(timezone.utc).isoformat(), 'tag': args.tag, 'base': BASE,
              'boundary': 'Explicit anonymous HTML resources over actual HTTP; no physical cold cache claim',
              'excludes': ['browser font selection', 'CSS descendant images/fonts', 'JS-triggered API reads',
                           'lazy page assets', 'browser cache waterfall and paint timings'],
              'requests': requests, 'declared_asset_count': len(assets.urls),
              'declared_asset_received_bytes': sum(row.get('received_entity_bytes', 0) for row in requests),
              'all_built_assets': sizes, 'all_built_asset_bytes': sum(row['bytes'] for row in sizes),
              'production_host_gate': False}
    with output.open('x', encoding='utf-8') as destination:
        json.dump(report, destination, ensure_ascii=False, indent=2)
        destination.write('\n')
    print(json.dumps({'tag': args.tag, 'homepage_ms': [row['ms'] for row in requests[:2]],
                      'declared_assets': len(assets.urls),
                      'declared_asset_received_bytes': report['declared_asset_received_bytes'],
                      'all_built_asset_bytes': report['all_built_asset_bytes']}))


if __name__ == '__main__':
    main()
