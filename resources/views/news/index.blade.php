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
                <h2 class="title title--small">2026</h2>
                @foreach ($news as $post)<p><a href="{{ route('news.show', $post['slug']) }}">{{ $post['title'] }}</a></p>@endforeach
            </div>
            <div class="wiki-page__content"><div class="news-index">
                @foreach ($news as $post)<div class="news-index__item">@include('home._user_news_post_preview', ['collapsed' => false])</div>@endforeach
            </div></div>
        </div>
    </div>
@endsection