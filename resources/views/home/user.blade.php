{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@extends('master')
@section('content')
    @include('home._user_header_default')
    <div class="osu-page">
        <div class="user-home">
            <div class="user-home__left-section">
                <div class="user-home__news">
                    <h2 class="user-home__left-title">新闻</h2>
                    @foreach ($news as $post)
                        @include('home._user_news_post_preview', ['post' => $post, 'collapsed' => $loop->iteration > 2])
                    @endforeach
                    <a href="{{ route('news.index') }}" class="user-home__news-posts-group user-home__news-posts-group--more">全部新闻</a>
                </div>
            </div>
            <div class="user-home__right-sidebar">
                <div class="user-home__buttons">
                    @include('home._user_giant_button', ['href' => route('download'), 'label' => '下载 OMS', 'icon' => 'download'])
                    @include('home._user_giant_button', ['href' => route('beatmapsets.index'), 'label' => '查找谱面', 'icon' => 'music', 'colour' => 'c-pink-darker'])
                    @include('home._user_giant_button', ['href' => route('forum.forums.index'), 'label' => '社区', 'icon' => 'comments', 'colour' => 'c-darkorange'])
                </div>
                <h3 class="user-home__beatmap-list-header">当前公开版本</h3>
                <div class="user-home__beatmapsets"><p>20260626 · Windows</p><p>支持 BMS 与 mania。IR 可在开发版中使用，公开版本尚未包含。</p><a href="/help">开始游玩</a></div>
            </div>
        </div>
    </div>
@endsection