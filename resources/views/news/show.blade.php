{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@extends('master', ['titlePrepend' => $post['title']])
@section('content')
    @include('home._user_header_default')
    <div class="osu-page osu-page--wiki">
        <div class="wiki-page">
            <nav class="wiki-page__toc" aria-label="新闻导航">
                <p><a href="{{ route('news.index') }}">← 全部新闻</a></p>
                <ul class="wiki-toc-list">
                    @foreach ($news as $other)
                        <li><a href="{{ route('news.show', $other['slug']) }}" @if ($other['slug'] === $post['slug']) aria-current="page" @endif>{{ $other['title'] }}</a></li>
                    @endforeach
                </ul>
            </nav>
            <div class="wiki-page__content"><article class="news-show">
                <div class="news-show__info"><time datetime="{{ $post['published_at'] }}">{{ $post['published_at'] }}</time><h1 class="news-show__title">{{ $post['title'] }}</h1></div>
                @foreach ($post['body'] as $paragraph)
                    @isset($paragraph['heading'])<h2>{{ $paragraph['heading'] }}</h2>@endisset
                    <p>{{ $paragraph['text'] }}</p>
                    @foreach ($paragraph['links'] ?? [] as $link)<p><a href="{{ $link['href'] }}">{{ $link['label'] }}</a></p>@endforeach
                @endforeach
            </article></div>
        </div>
    </div>
@endsection
