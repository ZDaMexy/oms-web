#!/bin/sh
# Build only on the task-owned F-disk Alpine WSL. No host package upgrade.
set -eu
web=/mnt/f/zdamexy-workspace/websites/oms-web
root="$web/.dev-cache/production-php/r4-root"
base="$web/.dev-cache/downloads/alpine-minirootfs-3.24.2-x86_64.tar.gz"
test "$(sha256sum "$base" | cut -d ' ' -f 1)" = c5ca053cfe1d85c5b96dff8b9bc57045f7f184a30ffb6b65776409ca90388677
if test "${1:-build}" = build; then
test ! -e "$root"
mkdir -p "$root" "$web/artifacts/production"
tar -xzf "$base" -C "$root"
# The mirror transports the official Alpine packages; APK verifies signatures
# against the keys carried by the fixed official minirootfs.
printf '%s\n' https://mirrors.tuna.tsinghua.edu.cn/alpine/v3.24/main https://mirrors.tuna.tsinghua.edu.cn/alpine/v3.24/community > "$root/etc/apk/repositories"
apk --root "$root" --no-cache --no-scripts upgrade --available
apk --root "$root" --initdb --no-cache --no-scripts add \
  php85=8.5.12-r0 php85-fpm=8.5.12-r0 \
  php85-intl=8.5.12-r0 php85-mbstring=8.5.12-r0 php85-ctype=8.5.12-r0 \
  php85-dom=8.5.12-r0 php85-fileinfo=8.5.12-r0 php85-iconv=8.5.12-r0 \
  php85-openssl=8.5.12-r0 php85-session=8.5.12-r0 php85-tokenizer=8.5.12-r0 \
  php85-curl=8.5.12-r0 php85-pdo=8.5.12-r0 php85-phar=8.5.12-r0 \
  php85-xml=8.5.12-r0 php85-xmlwriter=8.5.12-r0 php85-xmlreader=8.5.12-r0 \
  php85-simplexml=8.5.12-r0
# The stable repository has not yet shipped curl's October HTTP/2 fix. Resolve
# just the reviewed, signed libcurl package from edge; never upgrade the root
# wholesale to edge. Its dependencies are already satisfied by Alpine 3.24.
apk --root "$root" --no-cache --no-scripts \
  --repository https://dl-cdn.alpinelinux.org/alpine/edge/main \
  add libcurl=8.23.0-r0
else
test "${1:-}" = pack
test -f "$root/lib/apk/db/installed"
fi
chroot "$root" /usr/bin/php85 -v
chroot "$root" /usr/bin/php85 -r '$v=curl_version(); if ($v["version"] !== "8.23.0" || !str_starts_with($v["ssl_version"], "OpenSSL/3.5.9")) { throw new RuntimeException("Unexpected cURL/OpenSSL runtime"); } echo json_encode($v), PHP_EOL;'
chroot "$root" /usr/bin/php85 -m > "$web/artifacts/production/php-modules.txt"
apk --root "$root" info -v --installed > "$web/artifacts/production/php-packages.txt"
# No Composer/Node/build caches, database, private archive or application lives here.
mkdir -p "$root/app" "$root/tmp" "$root/run" "$root/dev" "$root/proc"
python3 "$web/scripts/package-php-runtime.py" "$root" "$web/artifacts/production/php85-8.5.12-alpine3243-curl8230.tar.gz"
sha256sum "$web/artifacts/production/php85-8.5.12-alpine3243-curl8230.tar.gz" > "$web/artifacts/production/php-runtime.sha256"
du -sk "$root"
