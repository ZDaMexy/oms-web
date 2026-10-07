{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@extends('master')
@section('content')
    @include('layout._page_header_v4', ['params' => ['theme' => 'error']])
    <div class="osu-page osu-page--generic text-center">
        <h1>{{ $omsError['status'] }}</h1><p>{{ $omsError['message'] }}</p>
        <p><a href="{{ rtrim(config('app.url'), '/').'/'.ltrim(request()->getRequestUri(), '/') }}">重试</a> · <a href="/">返回首页</a></p>
    </div>
@endsection
