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
    @include('layout._page_header_v4', ['params' => ['theme' => 'forum', 'links' => [
        ['active' => true, 'title' => '社区', 'url' => route('forum.forums.index')],
        ['title' => '发布帖子', 'url' => route('forum.topics.create')],
    ]]])
    <div class="osu-page osu-page--forum">
        <div class="forum-title forum-title--forum"><h1 class="forum-title__name">社区</h1><p class="forum-title__description">讨论、求助与分享。</p></div>
        <form action="{{ route('forum.forums.index') }}" method="GET" class="forum-list__buttons forum-list__buttons--search">
            <input class="account-edit-entry__input" aria-label="搜索帖子" name="q" value="{{ $context['q'] }}" maxlength="80" placeholder="搜索标题和正文">
            <select class="account-edit-entry__input" aria-label="帖子分类" name="category"><option value="">全部分类</option>@foreach ($categories as $key => $label)<option value="{{ $key }}" @selected(($context['category'] ?? '') === $key)>{{ $label }}</option>@endforeach</select>
            @isset($context['author_id'])<input type="hidden" name="author_id" value="{{ $context['author_id'] }}">@endisset
            <button class="btn-osu-big" type="submit"><span class="btn-osu-big__content">搜索</span></button>
            <a class="btn-osu-big btn-osu-big--forum-primary" href="{{ route('forum.topics.create') }}"><span class="btn-osu-big__content">发布帖子</span></a>
        </form>
        <div class="forum-list"><ul class="forum-list__items">
            @foreach ($posts['items'] as $post)
                @include('forum.forums._topic')
            @endforeach
        </ul></div>
        @if (count($posts['items']) === 0)<p>{{ $posts['total'] === 0 ? '还没有找到帖子，可以换个关键词或分类再试。' : '本页没有帖子，请返回第一页。' }}</p>@endif
        @include('oms._pagination', ['pagination' => $posts])
    </div>
    @include('oms._page_data')
@endsection
