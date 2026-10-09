"""Generate explicit native-app units and Nginx routes for one immutable release."""
import argparse
from pathlib import Path
import re

parser = argparse.ArgumentParser()
parser.add_argument('--release', type=Path, required=True)
parser.add_argument('--runtime', type=Path, required=True)
parser.add_argument('--work', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--staging', action='store_true')
args = parser.parse_args()
release, runtime, work, output = args.release, args.runtime, args.work, args.output
assert re.fullmatch(r'/opt/oms-ir/releases/[0-9a-f]{12}-[0-9a-f]{12}', str(release))
assert re.fullmatch(r'/opt/oms-web/runtime/php85-[0-9a-f]{12}', str(runtime))
assert str(work).startswith('/opt/oms-web/acceptance/') if args.staging else str(work).startswith('/var/cache/oms-web/')
output.mkdir(parents=True, exist_ok=False)
api_port, fpm_port, url = (18084, 19070, 'http://127.0.0.1:18090') if args.staging else (8081, 9070, 'https://oms.zdamexy.work')
fpm = (release / 'web/deploy/php-fpm.conf').read_text().replace('127.0.0.1:9070', f'127.0.0.1:{fpm_port}')
(output / 'php-fpm.conf').write_text(fpm)
# /app is identical in CLI and FPM namespaces. Only runtime cache/log directories
# are writable. No live database, backup or historical projection is mounted.
common = f'''User=oms-web
Group=oms-web
RootDirectory={runtime}
WorkingDirectory=/app
BindReadOnlyPaths={release}/web:/app {output}/php-fpm.conf:/etc/php85/oms-fpm.conf
BindPaths={work}/bootstrap:/app/bootstrap/cache {work}/storage:/app/storage
Environment=APP_ENV=production APP_DEBUG=false APP_URL={url} OMS_API_BASE=http://127.0.0.1:{api_port}
Environment=TMPDIR=/tmp
NoNewPrivileges=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectSystem=strict
ProtectHome=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
IPAddressDeny=any
IPAddressAllow=localhost
MemorySwapMax=0
TasksMax=32
UMask=0077
'''
runtime_lifecycle = 'Type=exec\nRemainAfterExit=yes\nRestart=no\n' if args.staging else 'Restart=on-failure\nRestartSec=2\n'
(output / 'oms-web.service').write_text(f'''[Unit]
Description=OMS native osu-web pages ({release.name})
After=network.target oms-ir.service
[Service]
{common}{runtime_lifecycle}ExecStart=/usr/sbin/php-fpm85 --nodaemonize --fpm-config /etc/php85/oms-fpm.conf
MemoryHigh=160M
MemoryMax=200M
CPUQuota=50%
[Install]
WantedBy=multi-user.target
''')
(output / 'oms-web-cache.service').write_text(f'''[Unit]
Description=Build OMS native caches inside the final app namespace
[Service]
Type=oneshot
RemainAfterExit=yes
{common}MemoryMax=128M
CPUQuota=50%
ExecStart=/usr/bin/php85 artisan config:cache
ExecStart=/usr/bin/php85 artisan view:cache
''')
headers = f'include {release}/web/deploy/nginx-headers.conf;'
api = ''
for version, catalog, timeout in [('v1', '/catalog/', 28), ('v1', '/', 15), ('v2', '/', 15)]:
    api += f'''location ^~ /api/ir/{version}{catalog} {{
    client_max_body_size 64k;
    error_page 413 = @oms_ir_body_too_large;
    proxy_pass http://127.0.0.1:{api_port};
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Connection "";
    proxy_connect_timeout 2s;
    proxy_read_timeout {timeout}s;
    proxy_buffering off;
    proxy_cache off;
    access_log off;
}}
'''
routes = f'''# Native OMS app. Include only in the already-approved BT OMS server.
{api}
location @oms_ir_body_too_large {{
    default_type application/json;
    add_header Cache-Control no-store always;
    add_header X-Content-Type-Options nosniff always;
    return 413 '{{"error":{{"code":"body_too_large","message":"Request exceeds 64 KiB"}}}}';
}}
location ^~ /assets/ {{
    root {release}/web/public;
    try_files $uri =404;
    autoindex off;
    add_header Cache-Control "public, max-age=31536000, immutable" always;
    {headers}
}}
location ^~ /images/ {{
    root {release}/web/public;
    try_files $uri =404;
    autoindex off;
    add_header Cache-Control no-cache always;
    {headers}
}}
location = /favicon.ico {{
    root {release}/web/public;
    try_files $uri =404;
    add_header Cache-Control no-cache always;
    {headers}
}}
location = /site.webmanifest {{
    root {release}/web/public;
    try_files $uri =404;
    add_header Cache-Control no-cache always;
    {headers}
}}
location = /omsir-openlr2.example.json {{
    root {release}/web/public;
    try_files $uri =404;
    default_type application/json;
    add_header Cache-Control no-cache always;
    {headers}
}}
location = /oms-web-source.tar.gz {{
    root {release}/web/public;
    try_files $uri =404;
    add_header Cache-Control no-cache always;
    {headers}
}}
location ^~ /ir/adapters/ {{
    proxy_pass http://127.0.0.1:{api_port};
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_connect_timeout 2s;
    proxy_read_timeout 15s;
    proxy_cache off;
    access_log off;
}}
location = /index.html {{ return 308 /$is_args$args; }}
location = /index.php {{ return 404; }}
location / {{
    include /www/server/nginx/conf/fastcgi_params;
    fastcgi_param SCRIPT_FILENAME /app/public/index.php;
    fastcgi_param SCRIPT_NAME /index.php;
    fastcgi_param DOCUMENT_ROOT /app/public;
    fastcgi_param HTTP_PROXY "";
    fastcgi_pass 127.0.0.1:{fpm_port};
    fastcgi_connect_timeout 2s;
    fastcgi_read_timeout 30s;
    add_header Cache-Control no-cache always;
    {headers}
}}
'''
(output / 'nginx-native.conf').write_text(routes)
if args.staging:
    (output / 'oms-web-nginx.service').write_text(f'''[Unit]
Description=Isolated native OMS HTTP acceptance ({release.name})
[Service]
Type=exec
RemainAfterExit=yes
Restart=no
User=oms-web
Group=oms-web
ExecStart=/www/server/nginx/sbin/nginx -e {work}/nginx-error.log -c {output}/nginx.conf -g "daemon off;"
MemoryHigh=80M
MemoryMax=96M
CPUQuota=25%
MemorySwapMax=0
TasksMax=16
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths={work}
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
IPAddressDeny=any
IPAddressAllow=localhost
UMask=0077
''')
    (output / 'nginx.conf').write_text(f'''pid {work}/nginx.pid;
error_log {work}/nginx-error.log warn;
worker_processes 1;
events {{ worker_connections 256; }}
http {{
lua_package_path "/www/server/nginx/lib/lua/?.lua;;";
include /www/server/nginx/conf/mime.types;
access_log off;
server_tokens off;
client_body_temp_path {work}/nginx-tmp;
proxy_temp_path {work}/nginx-tmp;
fastcgi_temp_path {work}/nginx-tmp;
gzip on;
gzip_types text/css application/javascript application/json image/svg+xml;
server {{
listen 127.0.0.1:18090;
server_name localhost;
include {output}/nginx-native.conf;
}}
}}
''')
