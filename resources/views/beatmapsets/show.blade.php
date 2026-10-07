{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@extends('master')
@section('content')
    <div class="js-react u-contents" data-react="beatmapset-page"></div>
    @include('oms._page_data')
    @include('layout._react_js', ['src' => 'js/beatmapsets-show.js'])
@endsection