# Licensed under AGPL-3.0-or-later; see LICENCE.
"""One explicit startup check of local pages; no polling or third-party requests."""
from datetime import datetime, timezone
import json
from pathlib import Path
import time

import httpx


root = Path(__file__).resolve().parents[1]
routes = ('/', '/news', '/download', '/help', '/credits', '/account', '/ir', '/rankings', '/community', '/ir/adapters/versions.json')
rows = []
ready = False
started = datetime.now(timezone.utc)
output = root / ('artifacts/startup-warm-' + started.strftime('%Y%m%d-%H%M%S-%f') + '.json')
with httpx.Client(base_url='http://127.0.0.1:8090', trust_env=False, timeout=35, follow_redirects=False) as client:
    try:
        for route in routes:
            began = time.monotonic()
            response = client.get(route)
            rows.append({'path': route, 'status': response.status_code, 'ms': round((time.monotonic() - began) * 1000, 3)})
            response.raise_for_status()
            if route.endswith('.json'):
                if 'items' not in response.json():
                    raise ValueError('The actual adapter manifest is missing')
            elif 'OMS' not in response.text:
                raise ValueError('The native page did not render')
        ready = True
    finally:
        output.write_text(json.dumps({'started_at': started.isoformat(), 'requests': rows,
                                      'all_pages_ready': ready,
                                      'one_local_startup_check': True, 'third_party_requests': False}, ensure_ascii=False, indent=2))
print('Local native pages and approved adapters are ready.')
