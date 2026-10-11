<?php

declare(strict_types=1);

// Run with the site's PHP 8.5 runtime: php85 scripts/verify-client-content.php.
// Exercises real routes without a server, account, database or network request.
// Fixtures, compiled views and logs stay inside .dev-cache/temp on the development disk.

use Illuminate\Contracts\Http\Kernel;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

const CONTENT_JSON_FLAGS = JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES;

$root = dirname(__DIR__);
require $root.'/vendor/autoload.php';

$scratch = $root.'/.dev-cache/temp/client-content-'.bin2hex(random_bytes(8));
$app = null;
$checks = 0;
$failed = false;

function check(bool $condition, string $message): void
{
    global $checks;
    if (!$condition) {
        throw new RuntimeException($message);
    }
    $checks++;
}

function getPage(string $path = '/client-content', string $method = 'GET', array $headers = [], array $cookies = []): Response
{
    global $kernel;
    $request = Request::create('http://localhost'.$path, $method, [], $cookies, [], [
        'HTTP_ACCEPT' => $path === '/client-content' ? 'application/json' : 'text/html',
    ]);
    foreach ($headers as $name => $value) {
        $request->headers->set($name, $value);
    }
    $response = $kernel->handle($request);
    $kernel->terminate($request, $response);

    return $response;
}

function publicCache(Response $response): void
{
    $headers = $response->headers;
    check($headers->hasCacheControlDirective('public') && $headers->getCacheControlDirective('max-age') === '300', 'Public cache must have max-age=300.');
    check(!$headers->hasCacheControlDirective('private') && !$headers->hasCacheControlDirective('no-cache') && !$headers->hasCacheControlDirective('no-store'), 'Public content must remain cacheable.');
    check($headers->getCookies() === [], 'Public content must not set cookies.');
    check(!$headers->has('Vary'), 'Public content must not vary by account or Cookie.');
}

function writeFixture(array $news, array $help): void
{
    global $scratch;
    foreach (['news' => $news, 'help' => $help] as $name => $items) {
        if (file_put_contents($scratch.'/resources/oms/'.$name.'.json', json_encode($items, CONTENT_JSON_FLAGS)) === false) {
            throw new RuntimeException('Cannot write public content fixture.');
        }
    }
}

function unavailable(string $name, string $etag): void
{
    $response = getPage(headers: ['If-None-Match' => $etag]);
    check($response->getStatusCode() === 503, $name.': expected explicit 503, not stale 304 or successful fallback.');
    $body = json_decode($response->getContent(), true, 32, JSON_THROW_ON_ERROR);
    check(($body['error']['code'] ?? null) === 'content_unavailable', $name.': expected content_unavailable.');
    check($response->headers->hasCacheControlDirective('no-store') && !$response->headers->has('ETag'), $name.': failure must not cache a new representation.');
    check($response->headers->getCookies() === [], $name.': failure must not set cookies.');
}

function removeFixture(string $directory): void
{
    // The caller supplies only the freshly created scratch directory.
    foreach (new FilesystemIterator($directory) as $entry) {
        if ($entry->isDir() && !$entry->isLink()) {
            removeFixture($entry->getPathname());
        } else {
            unlink($entry->getPathname());
        }
    }
    rmdir($directory);
}

try {
    foreach (['resources/oms', 'storage/framework/views', 'storage/logs', 'bootstrap/cache'] as $directory) {
        if (!mkdir($scratch.'/'.$directory, 0777, true)) {
            throw new RuntimeException('Cannot create isolated content fixture directory.');
        }
    }
    foreach (['APP_CONFIG_CACHE', 'APP_ROUTES_CACHE', 'APP_SERVICES_CACHE', 'APP_PACKAGES_CACHE', 'APP_EVENTS_CACHE'] as $name) {
        // Relative to the real application root, including on Windows.
        $value = substr($scratch, strlen($root) + 1).'/bootstrap/cache/'.$name.'.php';
        putenv($name.'='.$value);
        $_ENV[$name] = $_SERVER[$name] = $value;
    }
    foreach (['APP_ENV' => 'testing', 'APP_URL' => 'http://localhost', 'APP_DEBUG' => 'false', 'OMS_API_BASE' => 'http://127.0.0.1:1'] as $name => $value) {
        putenv($name.'='.$value);
        $_ENV[$name] = $_SERVER[$name] = $value;
    }

    $app = require $root.'/bootstrap/app.php';
    $app->useEnvironmentPath($scratch); // No real .env or credentials are read.
    $app->useStoragePath($scratch.'/storage');
    $app->usePublicPath($root.'/public');
    // AppServiceProvider resolves the URL generator while booting.
    $app->instance('request', Request::create('http://localhost/client-content'));
    $kernel = $app->make(Kernel::class);
    $kernel->bootstrap();

    $news = json_decode(file_get_contents($root.'/resources/oms/news.json'), true, 32, JSON_THROW_ON_ERROR);
    $help = json_decode(file_get_contents($root.'/resources/oms/help.json'), true, 32, JSON_THROW_ON_ERROR);
    usort($news, fn (array $left, array $right) => strcmp($right['published_at'], $left['published_at']));

    $response = getPage();
    check($response->getStatusCode() === 200, 'The real content route must return 200.');
    $body = $response->getContent();
    check(strlen($body) <= 262144, 'Content response exceeds 256 KiB.');
    check(str_starts_with($response->headers->get('Content-Type', ''), 'application/json'), 'Content response must be JSON.');
    check(json_decode($body, true, 32, JSON_THROW_ON_ERROR) === ['version' => 1, 'news' => $news, 'help' => $help], 'Versioned content must contain complete, unchanged source bodies.');
    $etag = '"'.hash('sha256', $body).'"';
    check($response->getEtag() === $etag, 'ETag must describe the actual response bytes.');
    publicCache($response);

    foreach ([$etag, 'W/'.$etag, '"different", W/'.$etag, '*'] as $conditional) {
        $cached = getPage(headers: ['If-None-Match' => $conditional]);
        check($cached->getStatusCode() === 304 && $cached->getContent() === '', 'Matching If-None-Match must return an empty 304.');
        check($cached->getEtag() === $etag, '304 must preserve the representation ETag.');
        publicCache($cached);
    }
    check(getPage(headers: ['If-None-Match' => '"different"'])->getContent() === $body, 'An unmatched ETag must return the full current body.');
    $head = getPage(method: 'HEAD');
    check($head->getStatusCode() === 200 && $head->getContent() === '' && $head->getEtag() === $etag, 'HEAD must have GET headers and no body.');
    publicCache($head);
    $withCookie = getPage(headers: ['Authorization' => 'Bearer fixture-only'], cookies: ['oms_access' => 'fixture-only', 'oms_refresh' => 'fixture-only']);
    check($withCookie->getContent() === $body && $withCookie->getEtag() === $etag, 'Cookie or Authorization must not alter public content.');
    publicCache($withCookie);
    check(getPage(method: 'POST')->getStatusCode() === 405, 'Content has no write endpoint.');

    $helpPage = getPage('/help');
    check($helpPage->getStatusCode() === 200, 'The real help route must render.');
    $html = $helpPage->getContent();
    foreach (['start', 'library', 'ir', 'scores', 'players', 'java-ir', 'openlr2-ir', 'feedback'] as $anchor) {
        check(str_contains($html, 'id="'.$anchor.'"'), 'Existing help anchor is missing: '.$anchor);
        check(in_array($anchor, array_column($help, 'id'), true), 'Published help ID must retain the existing anchor: '.$anchor);
    }
    foreach ($help as $section) {
        check(str_contains($html, 'href="#'.$section['id'].'"'), 'Help table of contents must link to the source ID.');
        check(str_contains($html, e($section['heading'])) && str_contains($html, e($section['text'])), 'Website help must render the shared heading and full text.');
        foreach ($section['links'] ?? [] as $link) {
            check(str_contains($html, 'href="'.e($link['href']).'"') && str_contains($html, e($link['label'])), 'Website help must render shared links.');
        }
    }
    check(str_contains($html, 'download="omsir.json"'), 'The existing OpenLR2 config download must remain a download.');
    foreach ($news as $post) {
        $page = getPage('/news/'.$post['slug']);
        check($page->getStatusCode() === 200, 'Existing news URL must still render: '.$post['slug']);
        foreach ($post['body'] as $paragraph) {
            check(str_contains($page->getContent(), e($paragraph['text'])), 'Website news must retain the same complete body as client content.');
            foreach ($paragraph['links'] ?? [] as $link) {
                if (str_starts_with($link['href'], '/help#')) {
                    check(in_array(substr($link['href'], strlen('/help#')), array_column($help, 'id'), true), 'News help fragments must resolve to a published help ID.');
                }
            }
        }
    }

    // Laravel resourcePath follows basePath; change it only after real page checks.
    // Config, routes, public assets, language and compiled-view paths are already loaded.
    $app->setBasePath($scratch);
    $mathHelp = [['id' => 'ir', 'heading' => '数学符号', 'text' => 'EX < 最大 EX，ACC > 0。', 'links' => [
        ['label' => '站内帮助', 'href' => '/help#ir'], ['label' => '反馈', 'href' => 'https://github.com/ZDaMexy/oms/issues'],
    ]]];
    writeFixture($news, $mathHelp);
    $math = getPage(headers: ['If-None-Match' => $etag]);
    check($math->getStatusCode() === 200 && $math->getEtag() !== $etag, 'Changed shared content must invalidate the old ETag.');
    check(json_decode($math->getContent(), true, 32, JSON_THROW_ON_ERROR)['help'] === $mathHelp, 'Pure text comparison signs and approved URL forms must survive unchanged.');
    $mathPage = getPage('/help');
    check($mathPage->getStatusCode() === 200 && str_contains($mathPage->getContent(), '<h2 id="ir">数学符号</h2>'), 'Renaming or moving a section must keep its source ID as the website anchor.');
    check(str_contains($mathPage->getContent(), e($mathHelp[0]['text'])), 'Website must escape pure text comparison signs.');

    $invalid = [
        'missing resource' => function (): void {
            global $scratch;
            unlink($scratch.'/resources/oms/help.json');
        },
        'malformed JSON' => function (): void {
            global $scratch;
            file_put_contents($scratch.'/resources/oms/news.json', '{');
        },
        'oversized source' => function (): void {
            global $scratch;
            file_put_contents($scratch.'/resources/oms/help.json', str_repeat(' ', 131073));
        },
        'empty help' => fn () => writeFixture($news, []),
        'missing help ID' => fn () => writeFixture($news, [['heading' => '章节', 'text' => '正文']]),
        'invalid help ID' => fn () => writeFixture($news, [[...$help[0], 'id' => '../ir']]),
        'duplicate help ID' => fn () => writeFixture($news, [$help[0], [...$help[1], 'id' => $help[0]['id']]]),
        'unknown account field' => fn () => writeFixture($news, [[...$help[0], 'owner_id' => 1]]),
        'HTML body' => fn () => writeFixture($news, [['id' => 'fixture', 'heading' => '格式错误', 'text' => '<b>正文</b>']]),
        'control character' => fn () => writeFixture($news, [['id' => 'fixture', 'heading' => '格式错误', 'text' => "正文\0"]]),
        'duplicate news slug' => fn () => writeFixture([$news[0], $news[0]], $help),
    ];
    foreach ($invalid as $name => $mutate) {
        writeFixture($news, $help);
        $mutate();
        unavailable($name, $etag);
    }
    foreach (['javascript:alert(1)', 'http://example.com/', '//example.com/', 'https://user:password@example.com/', '/help%xx', '/help path', '/\\example.com/', '/help"'] as $href) {
        writeFixture($news, [['id' => 'fixture', 'heading' => '链接', 'text' => '正文', 'links' => [['label' => '错误链接', 'href' => $href]]]]);
        unavailable('invalid URL '.$href, $etag);
    }

    // Each source can fit 128 KiB while their versioned envelope exceeds 256 KiB.
    $largeNews = $largeHelp = [];
    for ($index = 0; $index < 26; $index++) {
        $text = str_repeat('x', $index === 25 ? 1 : 5000);
        $largeNews[] = ['slug' => 'fixture-'.$index, 'published_at' => '2026-10-11', 'title' => 'N', 'image' => null, 'excerpt' => 'N', 'body' => [['text' => $text]]];
        $largeHelp[] = ['id' => 'fixture-'.$index, 'heading' => 'H'.$index, 'text' => $text];
    }
    $largeNews[25]['body'][0]['text'] .= str_repeat('x', 131072 - strlen(json_encode($largeNews, CONTENT_JSON_FLAGS)));
    $largeHelp[25]['text'] .= str_repeat('x', 131072 - strlen(json_encode($largeHelp, CONTENT_JSON_FLAGS)));
    check(strlen($largeNews[25]['body'][0]['text']) <= 6000 && strlen($largeHelp[25]['text']) <= 6000, 'Oversized response fixture must satisfy per-paragraph limits.');
    check(strlen(json_encode($largeNews, CONTENT_JSON_FLAGS)) === 131072 && strlen(json_encode($largeHelp, CONTENT_JSON_FLAGS)) === 131072, 'Oversized response fixture must satisfy source byte budgets.');
    writeFixture($largeNews, $largeHelp);
    unavailable('oversized combined response', $etag);

    fwrite(STDOUT, 'client-content: '.$checks." focused checks passed; anonymous routes and shared content verified.\n");
} catch (Throwable $error) {
    fwrite(STDERR, 'client-content: '.$error->getMessage()."\n");
    $failed = true;
} finally {
    try {
        $app?->setBasePath($root);
        if (is_dir($scratch)) {
            $resolvedScratch = realpath($scratch);
            if ($resolvedScratch === false
                || dirname($resolvedScratch) !== realpath($root.'/.dev-cache/temp')
                || preg_match('/^client-content-[0-9a-f]{16}$/D', basename($resolvedScratch)) !== 1) {
                throw new RuntimeException('Refusing to remove a fixture outside the intended scratch directory.');
            }
            removeFixture($resolvedScratch);
        }
    } catch (Throwable $error) {
        fwrite(STDERR, 'client-content cleanup: '.$error->getMessage()."\n");
        $failed = true;
    }
}

exit($failed ? 1 : 0);
