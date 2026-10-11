<?php

// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Libraries\OmsApiException;
use Illuminate\Http\Request;
use Illuminate\View\View;
use JsonException;
use Symfony\Component\HttpFoundation\Response;

class HomeController extends OmsController
{
    private const RESOURCE_BYTES = 131072;
    private const RESPONSE_BYTES = 262144;

    public function index(): View
    {
        $news = $this->newsPosts();

        return $this->page('home.user', 'home', ['news' => $news], ['news' => $news]);
    }

    public function newsIndex(): View
    {
        $news = $this->newsPosts();

        return $this->page('news.index', 'news-index', ['news' => $news], ['news' => $news]);
    }

    public function newsShow(string $slug): View
    {
        $news = $this->newsPosts();
        foreach ($news as $post) {
            if ($post['slug'] === $slug) {
                return $this->page('news.show', 'news-show', ['post' => $post], [
                    'post' => $post,
                    'news' => $news,
                    'titlePrepend' => $post['title'],
                ]);
            }
        }

        abort(404, '这篇新闻不存在。');
    }

    public function getDownload(): View
    {
        return $this->page('home.download', 'download', ['release_url' => config('oms.release_url')]);
    }

    public function help(): View
    {
        return $this->page('wiki.show', 'help', ['help' => $this->helpSections()]);
    }

    public function clientContent(Request $request): Response
    {
        try {
            $body = json_encode([
                'version' => 1,
                'news' => $this->newsPosts(),
                'help' => $this->helpSections(),
            ], JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
            if (strlen($body) > self::RESPONSE_BYTES) {
                $this->invalidContent();
            }
        } catch (OmsApiException $error) {
            return response()->json(['error' => [
                'code' => $error->errorCode,
                'message' => $error->getMessage(),
            ]], 503, ['Cache-Control' => 'no-store']);
        }

        $response = new Response($body, 200, [
            'Content-Type' => 'application/json; charset=UTF-8',
            'Cache-Control' => 'public, max-age=300',
        ]);
        $response->setEtag(hash('sha256', $body));
        $response->isNotModified($request);

        return $response;
    }

    private function newsPosts(): array
    {
        $posts = $this->readContent('news');
        $slugs = [];
        foreach ($posts as $post) {
            $this->fields($post, ['slug', 'published_at', 'title', 'image', 'excerpt', 'body']);
            if (!is_string($post['slug']) || preg_match('/^[A-Za-z0-9_-]{1,120}$/D', $post['slug']) !== 1
                || isset($slugs[$post['slug']])) {
                $this->invalidContent();
            }
            $slugs[$post['slug']] = true;
            if (!is_string($post['published_at']) || preg_match('/^(\d{4})-(\d{2})-(\d{2})$/D', $post['published_at'], $date) !== 1
                || !checkdate((int) $date[2], (int) $date[3], (int) $date[1])) {
                $this->invalidContent();
            }
            $this->plainText($post['title'], 200);
            $this->plainText($post['excerpt'], 1000);
            if ($post['image'] !== null) {
                $this->contentUrl($post['image']);
            }
            if (!is_array($post['body']) || !array_is_list($post['body']) || count($post['body']) < 1 || count($post['body']) > 32) {
                $this->invalidContent();
            }
            foreach ($post['body'] as $paragraph) {
                $this->paragraph($paragraph, false);
            }
        }
        usort($posts, fn (array $left, array $right) => strcmp($right['published_at'], $left['published_at']));

        return $posts;
    }

    private function helpSections(): array
    {
        $sections = $this->readContent('help');
        if ($sections === []) {
            $this->invalidContent();
        }
        $ids = [];
        foreach ($sections as $section) {
            $this->paragraph($section, true);
            if (!is_string($section['id']) || preg_match('/^[a-z][a-z0-9-]{0,63}$/D', $section['id']) !== 1
                || isset($ids[$section['id']])) {
                $this->invalidContent();
            }
            $ids[$section['id']] = true;
        }

        return $sections;
    }

    private function readContent(string $name): array
    {
        $path = resource_path('oms/'.$name.'.json');
        if (!is_file($path) || !is_readable($path)) {
            $this->invalidContent();
        }
        $bytes = file_get_contents($path, false, null, 0, self::RESOURCE_BYTES + 1);
        if ($bytes === false || strlen($bytes) > self::RESOURCE_BYTES) {
            $this->invalidContent();
        }
        try {
            $items = json_decode($bytes, true, 32, JSON_THROW_ON_ERROR);
        } catch (JsonException) {
            $this->invalidContent();
        }
        if (!is_array($items) || !array_is_list($items) || count($items) > 32) {
            $this->invalidContent();
        }

        return $items;
    }

    private function fields(mixed $value, array $required, array $optional = []): void
    {
        if (!is_array($value) || array_is_list($value)
            || array_diff($required, array_keys($value)) !== []
            || array_diff(array_keys($value), [...$required, ...$optional]) !== []) {
            $this->invalidContent();
        }
    }

    private function paragraph(mixed $paragraph, bool $helpSection): void
    {
        $this->fields($paragraph, $helpSection ? ['id', 'heading', 'text'] : ['text'], $helpSection ? ['links'] : ['heading', 'links']);
        $this->plainText($paragraph['text'], 6000);
        if (array_key_exists('heading', $paragraph)) {
            $this->plainText($paragraph['heading'], 200);
        }
        if (!array_key_exists('links', $paragraph)) {
            return;
        }
        if (!is_array($paragraph['links']) || !array_is_list($paragraph['links']) || count($paragraph['links']) > 16) {
            $this->invalidContent();
        }
        foreach ($paragraph['links'] as $link) {
            $this->fields($link, ['label', 'href']);
            $this->plainText($link['label'], 200);
            $this->contentUrl($link['href']);
        }
    }

    private function plainText(mixed $value, int $limit): void
    {
        if (!is_string($value) || trim($value) === '' || mb_strlen($value) > $limit
            || preg_match('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/', $value) === 1
            || preg_match('/<(?:\/?[a-z][\w:-]*(?:\s[^<>]*|\/?)>|!--|!doctype\b|\?)/iu', $value) === 1) {
            $this->invalidContent();
        }
    }

    private function contentUrl(mixed $value): void
    {
        if (!is_string($value) || strlen($value) > 2048 || preg_match('/[\x00-\x20\x7F]/', $value) === 1
            || strpbrk($value, "\\\"'") !== false || preg_match('/%(?![0-9a-f]{2})/i', $value) === 1) {
            $this->invalidContent();
        }
        $parts = parse_url($value);
        if ($parts === false) {
            $this->invalidContent();
        }
        $relative = str_starts_with($value, '/') && !str_starts_with($value, '//')
            && !isset($parts['scheme']) && !isset($parts['host']);
        $https = ($parts['scheme'] ?? null) === 'https' && isset($parts['host'])
            && !isset($parts['user']) && !isset($parts['pass']) && filter_var($value, FILTER_VALIDATE_URL) !== false;
        if (!$relative && !$https) {
            $this->invalidContent();
        }
    }

    private function invalidContent(): never
    {
        throw new OmsApiException(503, 'content_unavailable', '新闻与帮助暂时无法读取，请稍后重试。');
    }
}
