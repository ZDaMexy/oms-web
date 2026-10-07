{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@include('layout._page_header_v4', ['params' => [
    'theme' => 'home',
    'links' => [
        ['active' => request()->routeIs('home'), 'title' => '首页', 'url' => route('home')],
        ['active' => request()->routeIs('news.*'), 'title' => '新闻', 'url' => route('news.index')],
        ['active' => request()->routeIs('download'), 'title' => '下载', 'url' => route('download')],
    ],
]])