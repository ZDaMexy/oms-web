$ErrorActionPreference = 'Stop'
$webDevelopmentRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
if ([System.IO.Path]::GetPathRoot($webDevelopmentRoot).TrimEnd('\') -ieq $env:SystemDrive) {
    throw 'OMS Web development storage must be on a non-system drive.'
}
$webCacheRoot = Join-Path $webDevelopmentRoot '.dev-cache'
foreach ($webCacheChild in @('temp', 'npm', 'yarn', 'composer', 'composer-cache', 'downloads')) {
    New-Item -ItemType Directory -Path (Join-Path $webCacheRoot $webCacheChild) -Force | Out-Null
}
$env:TEMP = Join-Path $webCacheRoot 'temp'
$env:TMP = $env:TEMP
$env:NPM_CONFIG_CACHE = Join-Path $webCacheRoot 'npm'
$env:YARN_CACHE_FOLDER = Join-Path $webCacheRoot 'yarn'
$env:COMPOSER_HOME = Join-Path $webCacheRoot 'composer'
$env:COMPOSER_CACHE_DIR = Join-Path $webCacheRoot 'composer-cache'
Write-Output ('OMS Web development storage: ' + $webCacheRoot)
