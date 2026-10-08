#!/usr/bin/env bash
# Local acceptance only. No production host, service, user data or buying.
set -euo pipefail
web_root="$(cd "$(dirname "$0")/.." && pwd)"
control="$web_root/.dev-cache/local-runtime"
backend_root="$(cd "$web_root/../../oms-server/oms-backend" && pwd)"
python="$web_root/.dev-cache/backend-venv/bin/python"
archive="/mnt/f/zdamexy-workspace/oms/artifacts/oms-ir-multisource-20261004/archive/lr2ir-public-v1.db"
mkdir -p "$control" "$web_root/artifacts" "$control/nginx-tmp"
export TMPDIR="$web_root/.dev-cache/temp"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$backend_root"
if [[ "${1:-}" == stop ]]; then
  stopping=()
  for service in nginx php-fpm backend catalog; do
    pid_file="$control/$service.pid"
    if [[ -f "$pid_file" ]]; then
      pid="$(cat "$pid_file")"
      if [[ -r "/proc/$pid/cmdline" ]] && grep -Fqa "$web_root" "/proc/$pid/cmdline"; then
        kill -TERM "$pid"
        stopping+=("$pid")
      fi
    fi
  done
  for pid in "${stopping[@]}"; do
    for ((attempt=0; attempt<100; attempt++)); do
      if [[ ! -r "/proc/$pid/cmdline" ]] || ! grep -Fqa "$web_root" "/proc/$pid/cmdline"; then break; fi
      sleep 0.1
    done
    if [[ -r "/proc/$pid/cmdline" ]] && grep -Fqa "$web_root" "/proc/$pid/cmdline"; then
      echo "Own local process $pid has not stopped; keep its data and diagnose before restarting."
      exit 1
    fi
  done
  exit 0
fi
[[ "${1:-start}" == start ]] || { echo "Use start or stop"; exit 2; }
for service in nginx php-fpm backend catalog; do
  if [[ -f "$control/$service.pid" ]] && kill -0 "$(cat "$control/$service.pid")" 2>/dev/null; then
    echo "Local runtime already has a live $service process; stop it first."
    exit 1
  fi
done
[[ -f "$web_root/public/assets/manifest.json" && -x "$python" && -f "$archive" ]]
cat > "$control/php-fpm.conf" <<EOF
[global]
pid = $control/php-fpm.pid
error_log = $web_root/artifacts/php-fpm.log
daemonize = yes
[oms-local]
user = nginx
group = nginx
listen = 127.0.0.1:9070
pm = ondemand
pm.max_children = 2
pm.process_idle_timeout = 20s
catch_workers_output = yes
clear_env = no
php_admin_value[memory_limit] = 96M
php_admin_flag[display_errors] = off
php_admin_flag[log_errors] = on
php_admin_value[error_log] = $web_root/artifacts/php-errors.log
php_admin_flag[opcache.enable] = on
php_admin_value[opcache.memory_consumption] = 32
php_admin_value[opcache.interned_strings_buffer] = 4
php_admin_value[opcache.max_accelerated_files] = 6000
php_admin_flag[opcache.validate_timestamps] = 0
php_admin_flag[opcache.enable_file_override] = 1
EOF
cat > "$control/nginx.conf" <<EOF
pid $control/nginx.pid;
error_log $web_root/artifacts/nginx-error.log warn;
worker_processes 1;
events { worker_connections 256; }
http {
  include /etc/nginx/mime.types;
  access_log off;
  server_tokens off;
  client_max_body_size 64k;
  client_body_temp_path $control/nginx-tmp;
  proxy_temp_path $control/nginx-tmp;
  fastcgi_temp_path $control/nginx-tmp;
  gzip on;
  gzip_types text/css application/javascript application/json image/svg+xml;
  server {
    listen 127.0.0.1:8090;
    server_name localhost;
    root $web_root/public;
    index index.php;
    add_header X-Content-Type-Options nosniff always;
    add_header Referrer-Policy same-origin always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' https://gingerrush.com https://pixeldrain.net https://bms.alvorna.com https://a.sayobot.cn; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'" always;
    location ~ "^/assets/.*\.[0-9a-f]{8}\.(js|css|woff2?|png|jpg|svg)$" {
      try_files \$uri =404;
      add_header Cache-Control "public, max-age=31536000, immutable";
      add_header X-Content-Type-Options nosniff always;
      add_header Referrer-Policy same-origin always;
      add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' https://gingerrush.com https://pixeldrain.net https://bms.alvorna.com https://a.sayobot.cn; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'" always;
    }
    location ^~ /api/ir/ {
      error_page 413 = @body_too_large;
      proxy_pass http://127.0.0.1:8081;
      proxy_set_header X-Forwarded-For \$remote_addr;
      proxy_set_header X-Forwarded-Proto \$scheme;
      proxy_set_header Host \$http_host;
      proxy_read_timeout 30s;
    }
    location @body_too_large {
      default_type application/json;
      add_header Cache-Control no-store always;
      add_header X-Content-Type-Options nosniff always;
      add_header Referrer-Policy same-origin always;
      return 413 '{"error":{"code":"body_too_large","message":"请求内容超过 64 KiB。"}}';
    }
    location / {
      try_files \$uri \$uri/ /index.php?\$query_string;
      add_header Cache-Control "no-cache";
      add_header X-Content-Type-Options nosniff always;
      add_header Referrer-Policy same-origin always;
      add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' https://gingerrush.com https://pixeldrain.net https://bms.alvorna.com https://a.sayobot.cn; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'" always;
    }
    location = /index.php {
      include /etc/nginx/fastcgi_params;
      fastcgi_param SCRIPT_FILENAME $web_root/public/index.php;
      fastcgi_param HTTP_PROXY "";
      fastcgi_pass 127.0.0.1:9070;
      add_header Cache-Control "no-cache";
      add_header X-Content-Type-Options nosniff always;
      add_header Referrer-Policy same-origin always;
      add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' https://gingerrush.com https://pixeldrain.net https://bms.alvorna.com https://a.sayobot.cn; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'" always;
    }
    location ~* \.php(?:/|$) { return 404; }
    location ~ /\. { deny all; }
  }
}
EOF
export APP_URL=http://127.0.0.1:8090 OMS_API_BASE=http://127.0.0.1:8081 APP_ENV=local APP_DEBUG=false
php85 artisan config:clear
php85 artisan view:clear
php85 artisan view:cache
php85 artisan config:cache
nginx -t -c "$control/nginx.conf"
php-fpm85 --test --fpm-config "$control/php-fpm.conf"
# A failed launch must stop its own children instead of leaving a partial runtime.
trap 'bash "$web_root/scripts/local-runtime.sh" stop' ERR
# Data is a fresh, task-owned local database; the historical projection is only read.
nohup "$python" -m oms_ir serve --db "$control/live.db" --archive "$archive" --public-origin http://127.0.0.1:8090 --trusted-loopback-proxy --web-directory "$control/legacy-ir" > "$web_root/artifacts/local-backend.log" 2>&1 &
echo $! > "$control/backend.pid"
nohup "$python" -m uvicorn oms_ir.catalog_worker:create_catalog_app --factory --host 127.0.0.1 --port 8082 --no-access-log > "$web_root/artifacts/local-catalog.log" 2>&1 &
echo $! > "$control/catalog.pid"
php-fpm85 --fpm-config "$control/php-fpm.conf"
nginx -c "$control/nginx.conf"
"$python" "$web_root/scripts/warm-local.py"
trap - ERR
echo "OMS Web local runtime: http://127.0.0.1:8090"
