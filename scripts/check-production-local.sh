#!/bin/sh
set -eu
cd /mnt/f/zdamexy-workspace/websites/oms-web
export TMPDIR="$PWD/.dev-cache/temp"
export npm_config_cache="$PWD/.dev-cache/npm"
mkdir -p artifacts/production
npm run typecheck > artifacts/production/typecheck.log 2>&1
npm run prod > artifacts/production/build.log 2>&1
php85 -l app/Libraries/OmsApi.php
php85 -l app/Providers/AppServiceProvider.php
bash scripts/local-runtime.sh stop
bash scripts/local-runtime.sh start > artifacts/production/local-restart.log 2>&1
.dev-cache/backend-venv/bin/python scripts/verify-local.py > artifacts/production/http-gates.log 2>&1
