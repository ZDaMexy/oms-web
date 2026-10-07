{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@extends('master', ['titlePrepend' => $post['title']])
@section('content')
    @include('home._user_header_default')
    <div class="osu-page osu-page--wiki">
        <div class="wiki-page">
            <div class="wiki-page__toc"><p><a href="{{ route('news.index') }}">全部新闻</a></p>
                @foreach ($news as $other)<p><a href="{{ route('news.show', $other['slug']) }}">{{ $other['title'] }}</a></p>@endforeach
            </div>
            <div class="wiki-page__content"><article class="news-show">
                <div class="news-show__info"><h1 class="news-show__title">{{ $post['title'] }}</h1><p>{{ $post['published_at'] }}</p></div>
                @foreach ($post['body'] as $paragraph)
                    @isset($paragraph['heading'])<h2>{{ $paragraph['heading'] }}</h2>@endisset
                    <p>{{ $paragraph['text'] }}</p>
                    @foreach ($paragraph['links'] ?? [] as $link)<p><a href="{{ $link['href'] }}">{{ $link['label'] }}</a></p>@endforeach
                @endforeach
            </article></div>
        </div>
    </div>
@endsection