{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@extends('master')
@php
    $posts = $omsData['posts'];
    $context = $omsData['context'];
    $categories = ['discussion' => '讨论', 'help' => '求助', 'showcase' => '分享', 'development' => '开发记录'];
@endphp
@section('content')
    @include('layout._page_header_v4', ['params' => ['theme' => 'forum']])
    <div class="osu-page osu-page--forum">
        <div class="forum-list__heading">
            <h1>帖子</h1>
            <a class="btn-osu-big btn-osu-big--forum-primary" href="{{ route('forum.topics.create') }}"><span class="btn-osu-big__content">发布帖子</span></a>
        </div>
        <form action="{{ route('forum.forums.index') }}" method="GET" class="forum-list__buttons forum-list__buttons--search">
            <input class="account-edit-entry__input" type="search" aria-label="搜索帖子" name="q" value="{{ $context['q'] }}" maxlength="80" placeholder="搜索帖子">
            <select class="account-edit-entry__input" aria-label="帖子分类" name="category"><option value="">全部分类</option>@foreach ($categories as $key => $label)<option value="{{ $key }}" @selected(($context['category'] ?? '') === $key)>{{ $label }}</option>@endforeach</select>
            @isset($context['author_id'])<input type="hidden" name="author_id" value="{{ $context['author_id'] }}">@endisset
            <button class="btn-osu-big" type="submit"><span class="btn-osu-big__content">搜索</span></button>
        </form>
        <div class="forum-list"><ul class="forum-list__items">
            @foreach ($posts['items'] as $post)
                @include('forum.forums._topic')
            @endforeach
        </ul></div>
        @if ($posts['items'] === [])
            <p class="forum-list__empty">
                @if ($posts['total'] > 0) 这一页没有帖子。
                @elseif ($context['q'] !== '' || isset($context['category']) || isset($context['author_id'])) 没有符合筛选的帖子。
                @else 还没有帖子。
                @endif
            </p>
        @endif
        @if ($posts['page'] > 1 || $posts['total'] > $posts['limit'])
            @include('oms._pagination', ['pagination' => $posts])
        @endif
    </div>
    @include('oms._page_data')
@endsection
