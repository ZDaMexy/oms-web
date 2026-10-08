{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@extends('master')
@section('content')
    @include('layout._page_header_v4', ['params' => ['theme' => 'forum', 'links' => [
        ['title' => '社区', 'url' => route('forum.forums.index')],
        ['active' => true, 'title' => '发布帖子', 'url' => route('forum.topics.create')],
    ]]])
    <div class="osu-page osu-page--forum-topic">
        <div class="forum-topic-title"><h1 class="forum-topic-title__title">发布帖子</h1></div>
        <p data-oms-auth="guest">登录 OMS 账号后即可发帖。登录入口在导航中。</p>
        @include('forum.topics._post_edit_form', ['kind' => 'post', 'id' => '', 'owner' => '', 'content' => '', 'postTitle' => '', 'category' => 'discussion'])
    </div>
    @include('oms._page_data')
@endsection
