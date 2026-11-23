{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@extends('master')
@section('content')
    @include('home._user_header_default')
    <div class="osu-page osu-page--wiki">
        <div class="wiki-page">
            <div class="wiki-page__toc">
                <nav aria-label="按年份浏览">
                    <ul class="wiki-toc-list">
                        @foreach (array_unique(array_map(fn ($post) => substr($post['published_at'], 0, 4), $news)) as $year)
                            <li><a href="#news-{{ $year }}">{{ $year }}</a></li>
                        @endforeach
                    </ul>
                </nav>
            </div>
            <div class="wiki-page__content"><div class="news-index">
                <h1 class="title">新闻</h1>
                @foreach ($news as $post)
                    @php($year = substr($post['published_at'], 0, 4))
                    @if ($loop->first || $year !== substr($news[$loop->index - 1]['published_at'], 0, 4))
                        <h2 id="news-{{ $year }}" class="title title--small">{{ $year }}</h2>
                    @endif
                    @include('home._user_news_post_preview')
                @endforeach
            </div></div>
        </div>
    </div>
@endsection
