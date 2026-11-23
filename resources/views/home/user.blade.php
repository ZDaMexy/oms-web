{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@extends('master')
@section('content')
    @include('home._user_header_default')
    <div class="osu-page">
        <section class="user-home__hero" aria-labelledby="home-title">
            <div class="user-home__intro">
                <h1 id="home-title">OMS</h1>
                <p>BMS 与 mania 音乐游戏</p>
                <div class="user-home__actions">
                    <a class="btn-osu-big user-home__download" href="{{ route('download') }}">
                        <i class="fas fa-download" aria-hidden="true"></i> 下载 Windows 版
                    </a>
                    <a class="user-home__browse" href="{{ route('beatmapsets.index') }}">查找谱面 <span aria-hidden="true">→</span></a>
                </div>
            </div>
            <div class="user-home__playfield" aria-hidden="true">
                <span></span><span></span><span></span><span></span><span></span><span></span><span></span>
            </div>
        </section>
        <div class="user-home">
            <section aria-labelledby="home-news">
                <div class="user-home__section-header">
                    <h2 id="home-news">最新新闻</h2>
                    <a href="{{ route('news.index') }}">全部新闻 <span aria-hidden="true">→</span></a>
                </div>
                @foreach (array_slice($news, 0, 3) as $post)
                    @include('home._user_news_post_preview', ['post' => $post])
                @endforeach
            </section>
            <nav class="user-home__links" aria-label="常用入口">
                <a href="{{ route('ir') }}"><i class="fas fa-list-ol" aria-hidden="true"></i> 谱面榜</a>
                <a href="{{ route('rankings') }}"><i class="fas fa-trophy" aria-hidden="true"></i> 玩家榜</a>
                <a href="{{ route('forum.forums.index') }}"><i class="fas fa-comments" aria-hidden="true"></i> 社区讨论</a>
                <a href="{{ route('help') }}"><i class="fas fa-book-open" aria-hidden="true"></i> 新手指南</a>
            </nav>
        </div>
    </div>
@endsection
