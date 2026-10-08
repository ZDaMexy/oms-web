// Licensed under AGPL-3.0-or-later; see LICENCE.
// Reacquire the legacy page's public fonts without changing its original archive.
import { createHash } from 'node:crypto';
import { existsSync } from 'node:fs';
import { copyFile, cp, mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const designatedRoot = 'F:/zdamexy-workspace/oms/artifacts/oms-web-migration-20261007/legacy-r3';
const legacyRoot = path.resolve(process.argv[2] ?? designatedRoot);
if (legacyRoot !== path.resolve(designatedRoot) || path.parse(legacyRoot).root.toLowerCase() !== 'f:\\') {
  throw new Error('Only the designated F-drive legacy-r3 recovery directory is accepted.');
}
if (process.argv.length > 3) throw new Error('Usage: node scripts/offline-legacy-fonts.mjs [LEGACY_R3]');

const originalRoot = path.join(legacyRoot, 'restore-original');
const fontRoot = path.join(legacyRoot, 'offline-fonts');
const offlineRoot = path.join(legacyRoot, 'restore-original-offline');
const coreReportPath = path.join(legacyRoot, 'recovery-report.json');
const reportPath = path.join(fontRoot, 'font-recovery-report.json');
const licenses = [
  ['Big Shoulders Display', 'bigshouldersdisplay'],
  ['JetBrains Mono', 'jetbrainsmono'],
  ['Noto Sans JP', 'notosansjp'],
  ['Noto Sans SC', 'notosanssc'],
];
const userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36';
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const cssUrlPattern = /url\(\s*(?:(['"])(.*?)\1|([^'")\s]+))\s*\)/g;
let report;

function assertPublicUrl(value, hostname) {
  const url = new URL(value);
  if (url.protocol !== 'https:' || url.hostname !== hostname || url.port || url.username || url.password) {
    throw new Error('A public font resource has an unexpected origin.');
  }
  return url;
}

async function download(value, hostname, limit) {
  const url = assertPublicUrl(value, hostname);
  const response = await fetch(url, {
    headers: { 'User-Agent': userAgent },
    redirect: 'error',
    signal: AbortSignal.timeout(55_000),
  });
  if (!response.ok) throw new Error('Font resource request failed: HTTP ' + response.status + ' at ' + url.hostname);
  if (!response.body) throw new Error('Font resource response has no body.');
  const reader = response.body.getReader();
  const chunks = [];
  let bytes = 0;
  for (;;) {
    const { done, value: chunk } = await reader.read();
    if (done) break;
    bytes += chunk.byteLength;
    if (bytes > limit) {
      await reader.cancel();
      throw new Error('Font resource exceeded its byte budget at ' + url.hostname);
    }
    chunks.push(Buffer.from(chunk));
  }
  return {
    data: Buffer.concat(chunks, bytes),
    fetchedAt: new Date().toISOString(),
    contentType: response.headers.get('content-type'),
    etag: response.headers.get('etag'),
  };
}

async function snapshotOriginal(relativeRoot = '') {
  const result = [];
  const entries = await readdir(path.join(originalRoot, relativeRoot), { withFileTypes: true });
  for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
    const relative = path.posix.join(relativeRoot, entry.name);
    if (entry.isSymbolicLink() || /(^|\/)(\.git|\.env(?:\..*)?)$/.test(relative)) {
      throw new Error('The original recovery contains an unexpected link or private file.');
    }
    if (entry.isDirectory()) result.push(...await snapshotOriginal(relative));
    else if (entry.isFile()) {
      const data = await readFile(path.join(originalRoot, relative));
      result.push({ path: relative, bytes: data.length, sha256: sha256(data) });
    } else throw new Error('The original recovery contains an unsupported entry.');
  }
  return result;
}

async function snapshotCoreFiles(core) {
  const artifacts = ['legacy.bundle', 'working-tree.patch', 'working-tree-status.bin', 'working-tree.tar.gz', 'original.tar.gz', 'published.tar.gz', 'head.tar.gz', 'published-runtime.tar.gz'];
  const result = [];
  for (const relative of artifacts) {
    const data = await readFile(path.join(legacyRoot, relative));
    const digest = sha256(data);
    const recorded = core.files.find((file) => file.path === relative);
    if (!recorded || digest !== recorded.sha256) throw new Error('The core recovery artifact differs: ' + relative);
    result.push({ path: relative, bytes: data.length, sha256: digest });
  }
  return result;
}

function fontExtension(data) {
  const signature = data.subarray(0, 4).toString('ascii');
  if (signature === 'wOF2') return '.woff2';
  if (signature === 'wOFF') return '.woff';
  if (signature === 'OTTO') return '.otf';
  if (data.length >= 4 && data.readUInt32BE(0) === 0x00010000) return '.ttf';
  throw new Error('A public font response is not a supported font file.');
}

async function main() {
  if (existsSync(fontRoot) || existsSync(offlineRoot)) throw new Error('Offline output already exists; preserve it and choose an explicitly reviewed recovery run.');
  const coreBytes = await readFile(coreReportPath);
  const core = JSON.parse(coreBytes);
  if (core.revisions.original !== 'e8b764bcbbc9a7c25c330f5a6b144692bb374dd5') throw new Error('Unexpected original design revision.');
  const coreBefore = await snapshotCoreFiles(core);
  const originalBefore = await snapshotOriginal();
  const htmlBytes = await readFile(path.join(originalRoot, 'index.html'));
  const html = htmlBytes.toString('utf8');
  const fontTags = [...html.matchAll(/<link\b[^>]*>/gi)].map((match) => match[0]).filter((tag) =>
    /\brel\s*=\s*(['"])stylesheet\1/i.test(tag) && /\bhref\s*=\s*(['"])https:\/\/fonts\.googleapis\.com\//i.test(tag));
  if (fontTags.length !== 1) throw new Error('Expected exactly one legacy Google Fonts stylesheet.');
  const sourceHref = fontTags[0].match(/\bhref\s*=\s*(['"])(.*?)\1/i)[2];
  const stylesheetUrl = assertPublicUrl(sourceHref.replace(/&amp;/g, '&'), 'fonts.googleapis.com');
  if (!['/css', '/css2'].includes(stylesheetUrl.pathname)) throw new Error('Unexpected Google Fonts CSS path.');
  const requestedFamilies = stylesheetUrl.searchParams.getAll('family').map((family) => {
    const [name, weights] = family.split(':wght@');
    if (!weights || !/^\d+(;\d+)*$/.test(weights)) throw new Error('Unexpected legacy font weight request.');
    return { name, weights: weights.split(';').map(Number) };
  });
  const expectedNames = licenses.map(([family]) => family).sort();
  if (JSON.stringify(requestedFamilies.map((family) => family.name).sort()) !== JSON.stringify(expectedNames)) {
    throw new Error('The legacy stylesheet does not request the four approved font families.');
  }
  await mkdir(path.join(fontRoot, 'fonts'), { recursive: true });
  await mkdir(path.join(fontRoot, 'licenses'));
  report = {
    complete: false,
    startedAt: new Date().toISOString(),
    originalRevision: core.revisions.original,
    historicalFontBytesVerified: false,
    provenanceBoundary: 'These public font bytes are acquired in this run, not evidence of the font bytes served in June 2026.',
    coreRecoveryReport: '../recovery-report.json',
    coreRecoveryReportSha256: sha256(coreBytes),
    scriptSha256: sha256(await readFile(fileURLToPath(import.meta.url))),
    sourceIndexSha256: sha256(htmlBytes),
    stylesheetUrl: stylesheetUrl.href,
    cssRequestUserAgent: userAgent,
    requestedFamilies,
    fonts: [],
    licenses: [],
  };
  await writeFile(reportPath, JSON.stringify(report, null, 2) + '\n');
  const cssDownload = await download(stylesheetUrl.href, 'fonts.googleapis.com', 8 * 1024 * 1024);
  const css = cssDownload.data.toString('utf8');
  const faces = [...css.matchAll(/@font-face\s*\{([^}]+)\}/g)].map((match) => {
    const body = match[1];
    const family = body.match(/\bfont-family\s*:\s*(?:'([^']+)'|"([^"]+)"|([^;]+))\s*;/);
    const weight = body.match(/\bfont-weight\s*:\s*([\d\s]+)\s*;/);
    if (!family || !weight) throw new Error('A Google Fonts face is missing its family or weight.');
    return { family: (family[1] ?? family[2] ?? family[3]).trim(), weights: weight[1].trim().split(/\s+/).map(Number) };
  });
  if (!faces.length || css.replace(/\/\*[\s\S]*?\*\//g, '').replace(/@font-face\s*\{[^}]+\}/g, '').trim()) {
    throw new Error('The public stylesheet contains unexpected rules.');
  }
  for (const requested of requestedFamilies) {
    const available = faces.filter((face) => face.family === requested.name);
    for (const weight of requested.weights) {
      if (!available.some((face) => face.weights.length === 1 ? face.weights[0] === weight : weight >= face.weights[0] && weight <= face.weights[1])) {
        throw new Error('The public stylesheet omitted a requested family or weight.');
      }
    }
  }
  if (faces.some((face) => !expectedNames.includes(face.family))) throw new Error('The public stylesheet added an unapproved family.');
  const sourceReferences = [...css.matchAll(cssUrlPattern)].map((match) => match[2] ?? match[3]);
  const uniqueUrls = [...new Set(sourceReferences)];
  if (!uniqueUrls.length || uniqueUrls.length > 2500) throw new Error('Unexpected public font resource count.');
  for (const value of uniqueUrls) {
    if (!assertPublicUrl(value, 'fonts.gstatic.com').pathname.startsWith('/s/')) throw new Error('Unexpected gstatic font path.');
  }
  report.originalStylesheet = { path: 'google-fonts.original.css', bytes: cssDownload.data.length, sha256: sha256(cssDownload.data), fetchedAt: cssDownload.fetchedAt, contentType: cssDownload.contentType, etag: cssDownload.etag };
  await writeFile(path.join(fontRoot, 'google-fonts.original.css'), cssDownload.data);
  for (const [family, directory] of licenses) {
    const url = 'https://raw.githubusercontent.com/google/fonts/main/ofl/' + directory + '/OFL.txt';
    const license = await download(url, 'raw.githubusercontent.com', 64 * 1024);
    if (!license.data.toString('utf8').includes('SIL OPEN FONT LICENSE Version 1.1')) throw new Error('A family license is not OFL 1.1.');
    const relative = 'licenses/' + directory + '-OFL.txt';
    await writeFile(path.join(fontRoot, relative), license.data);
    report.licenses.push({ family, url, path: relative, bytes: license.data.length, sha256: sha256(license.data), fetchedAt: license.fetchedAt });
  }
  const localNames = new Map();
  let totalFontBytes = 0;
  for (let offset = 0; offset < uniqueUrls.length; offset += 4) {
    const acquired = await Promise.all(uniqueUrls.slice(offset, offset + 4).map(async (url) => {
      const downloaded = await download(url, 'fonts.gstatic.com', 32 * 1024 * 1024);
      const digest = sha256(downloaded.data);
      const filename = digest + fontExtension(downloaded.data);
      await writeFile(path.join(fontRoot, 'fonts', filename), downloaded.data);
      localNames.set(url, filename);
      return { url, path: 'fonts/' + filename, bytes: downloaded.data.length, sha256: digest, fetchedAt: downloaded.fetchedAt, contentType: downloaded.contentType, etag: downloaded.etag };
    }));
    report.fonts.push(...acquired);
    totalFontBytes += acquired.reduce((sum, font) => sum + font.bytes, 0);
    if (totalFontBytes > 256 * 1024 * 1024) throw new Error('The complete font archive exceeded its 256 MiB budget.');
    await writeFile(reportPath, JSON.stringify(report, null, 2) + '\n');
    if (offset === 0 || offset + 4 >= uniqueUrls.length || offset % 100 === 0) {
      process.stdout.write(JSON.stringify({ fontResourcesArchived: report.fonts.length, totalFontResources: uniqueUrls.length, bytes: totalFontBytes }) + '\n');
    }
  }
  const localCss = css.replace(cssUrlPattern, (_match, _quote, quoted, bare) => 'url("fonts/' + localNames.get(quoted ?? bare) + '")');
  const localReferences = [...localCss.matchAll(cssUrlPattern)].map((match) => match[2] ?? match[3]);
  if (localReferences.length !== sourceReferences.length) throw new Error('The offline stylesheet changed its resource count.');
  for (const relative of new Set(localReferences)) {
    if (!/^fonts\/[a-f0-9]{64}\.(woff2?|ttf|otf)$/.test(relative)) throw new Error('The offline stylesheet retained a nonlocal reference.');
    const record = report.fonts.find((font) => font.path === relative);
    if (!record || sha256(await readFile(path.join(fontRoot, relative))) !== record.sha256) throw new Error('An offline font reference does not resolve exactly.');
  }
  await writeFile(path.join(fontRoot, 'fonts.css'), localCss);
  await cp(originalRoot, offlineRoot, { recursive: true, force: false, errorOnExist: true });
  const siteFonts = path.join(offlineRoot, 'offline-fonts');
  await mkdir(path.join(siteFonts, 'fonts'), { recursive: true });
  await mkdir(path.join(siteFonts, 'licenses'));
  const copiedResources = ['fonts.css', ...report.licenses.map((license) => license.path), ...new Set(report.fonts.map((font) => font.path))];
  for (const relative of copiedResources) {
    await copyFile(path.join(fontRoot, relative), path.join(siteFonts, relative));
    if (sha256(await readFile(path.join(siteFonts, relative))) !== sha256(await readFile(path.join(fontRoot, relative)))) {
      throw new Error('An offline site font resource differs from its archive.');
    }
  }
  let removedPreconnects = 0;
  const offlineHtml = html.replace(fontTags[0], fontTags[0].replace(/\bhref\s*=\s*(['"])(.*?)\1/i, 'href="offline-fonts/fonts.css"'))
    .replace(/<link\b[^>]*>/gi, (tag) => {
      if (/\brel\s*=\s*(['"])preconnect\1/i.test(tag) && /\bhref\s*=\s*(['"])https:\/\/fonts\.(googleapis|gstatic)\.com(?:\/)?\1/i.test(tag)) {
        removedPreconnects++;
        return '';
      }
      return tag;
    });
  if (/<link\b[^>]*\bhref\s*=\s*(['"])https:\/\/fonts\.(googleapis|gstatic)\.com/i.test(offlineHtml)) throw new Error('The offline page retained a remote font link.');
  await writeFile(path.join(offlineRoot, 'index.html'), offlineHtml);
  for (const original of originalBefore.filter((file) => file.path !== 'index.html')) {
    if (sha256(await readFile(path.join(offlineRoot, original.path))) !== original.sha256) throw new Error('An original offline copy file changed: ' + original.path);
  }
  if (JSON.stringify(await snapshotOriginal()) !== JSON.stringify(originalBefore) || JSON.stringify(await snapshotCoreFiles(core)) !== JSON.stringify(coreBefore) || sha256(await readFile(coreReportPath)) !== sha256(coreBytes)) {
    throw new Error('An immutable core archive or original recovery changed.');
  }
  report.completedAt = new Date().toISOString();
  report.sourceArchiveAndRestoreUnchanged = true;
  report.coreArtifactsVerified = coreBefore;
  report.originalFilesVerified = originalBefore.length;
  report.offlineCopy = '../restore-original-offline';
  report.offlineIndexSha256 = sha256(Buffer.from(offlineHtml));
  report.localStylesheet = { path: 'fonts.css', bytes: Buffer.byteLength(localCss), sha256: sha256(Buffer.from(localCss)) };
  report.sourceFontReferences = sourceReferences.length;
  report.allFontReferencesResolveLocally = true;
  report.uniqueFontResources = uniqueUrls.length;
  report.totalFontBytes = totalFontBytes;
  const storedFonts = new Map(report.fonts.map((font) => [font.path, font.bytes]));
  report.uniqueStoredFontFiles = storedFonts.size;
  report.storedFontBytes = [...storedFonts.values()].reduce((sum, bytes) => sum + bytes, 0);
  report.removedGoogleFontPreconnects = removedPreconnects;
  const note = '# 原介绍页字体离线补充\n\n本次公开字体获取完成于 ' + report.completedAt
    + '。这些字节不是 2026 年 6 月历史字体字节的证据；原归档、原恢复和其报告保持不变。\n\n'
    + '核心恢复证据：[recovery-report.json](../recovery-report.json)。字体来源、获取时间、SHA、完整引用校验和本脚本身份见 [font-recovery-report.json](font-recovery-report.json)。\n\n'
    + '离线页面副本在 [restore-original-offline](../restore-original-offline/index.html)，从该目录启动静态服务器打开 /。只替换 Google Fonts stylesheet 并移除对应 preconnect；其他原文件保持原字节。\n\n'
    + '原 Google Fonts CSS 保存在 google-fonts.original.css；实际离线副本只加载 fonts.css 及其全部本地字体文件。该静态引用检查不代签浏览器实际字体选择或像素验收。\n\n'
    + '四个字体家族使用 SIL OFL 1.1，版权和许可原件保存在 licenses/。许可证不改为 AGPL，不把字体作者用作 OMS 背书。\n';
  await writeFile(path.join(fontRoot, 'README.md'), note);
  report.complete = true;
  await writeFile(reportPath, JSON.stringify(report, null, 2) + '\n');
  process.stdout.write(JSON.stringify({ complete: true, report: reportPath, offlineCopy: offlineRoot, uniqueFontResources: uniqueUrls.length, fontBytes: totalFontBytes, storedFontBytes: report.storedFontBytes, historicalFontBytesVerified: false }) + '\n');
}

try {
  await main();
} catch (error) {
  if (report && !report.complete) {
    report.failedAt = new Date().toISOString();
    report.failure = error.message;
    await writeFile(reportPath, JSON.stringify(report, null, 2) + '\n');
  }
  process.stderr.write('Offline font recovery failed: ' + error.message + '\n');
  process.exitCode = 1;
}
