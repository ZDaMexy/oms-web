#!/usr/bin/env bash
# OMS assets and view compilation. Does not start services or change OMS data.
set -euo pipefail
cd "$(dirname "$0")"
[[ "$(pwd)" == /mnt/f/* ]] || { echo 'Build this checkout on F, after UseDevelopmentStorage.ps1.'; exit 1; }
export COMPOSER_ALLOW_SUPERUSER=1 COMPOSER_NO_INTERACTION=1
export COMPOSER_HOME="$PWD/.dev-cache/composer" COMPOSER_CACHE_DIR="$PWD/.dev-cache/composer-cache"
export npm_config_cache="$PWD/.dev-cache/npm" TMPDIR="$PWD/.dev-cache/temp"
export NODE_OPTIONS=--max-old-space-size=1024
mkdir -p "$TMPDIR" artifacts
composer install --no-dev --prefer-dist --no-progress
npm ci --no-fund
npm run typecheck
npm run production
php85 artisan view:clear
php85 artisan view:cache