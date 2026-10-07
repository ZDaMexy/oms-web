<?php

// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

declare(strict_types=1);

namespace App\Http\Controllers;

use Illuminate\View\View;
use LogicException;

class HomeController extends OmsController
{
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

    private function newsPosts(): array
    {
        $path = resource_path('oms/news.json');
        if (!is_file($path)) {
            throw new LogicException('OMS 新闻资源缺失。');
        }
        $posts = json_decode(file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);
        if (!is_array($posts) || !array_is_list($posts)) {
            throw new LogicException('OMS 新闻资源必须为文章列表。');
        }
        usort($posts, fn (array $left, array $right) => strcmp($right['published_at'], $left['published_at']));

        return $posts;
    }
}
