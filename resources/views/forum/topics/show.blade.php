{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@extends('master', ['titlePrepend' => $omsData['post']['post']['title']])
@php
    $post = $omsData['post']['post'];
    $replies = $omsData['replies'];
@endphp
@section('content')
    @include('layout._page_header_v4', ['params' => ['theme' => 'forum', 'links' => [
        ['title' => '社区', 'url' => route('forum.forums.index')],
        ['active' => true, 'title' => $post['title'], 'url' => route('forum.topics.show', $post['id'])],
    ]]])
    <div class="osu-page osu-page--forum-topic">
        <div class="forum-topic-title"><div class="forum-topic-title__item forum-topic-title__item--main">
            <h1 class="forum-topic-title__title">{{ $post['title'] }}</h1>
            <p class="forum-topic-title__post-time">{!! timeago(new DateTimeImmutable($post['created_at'])) !!}</p>
        </div><div class="forum-topic-title__item forum-topic-title__item--counters">{{ $post['reply_count'] }} 回复</div></div>
        @include('forum.topics._post', ['entry' => $post, 'kind' => 'post'])
        @foreach ($replies['items'] as $reply)@include('forum.topics._post', ['entry' => $reply, 'kind' => 'reply'])@endforeach
        @include('oms._pagination', ['pagination' => $replies])
        @if (!$post['deleted'])
            <h2 class="title">回复</h2>
            <p data-oms-auth="guest">请先登录后回复。</p>
            @include('forum.topics._post_edit_form', ['kind' => 'reply', 'id' => $post['id'], 'owner' => '', 'content' => ''])
        @endif
    </div>
    @include('oms._page_data')
@endsection
