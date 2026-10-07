<?php

// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::middleware('web')->group(function (): void {
    Route::get('/', 'HomeController@index')->name('home');
    Route::get('home', 'HomeController@index');
    Route::get('news', 'HomeController@newsIndex')->name('news.index');
    Route::get('news/{slug}', 'HomeController@newsShow')->name('news.show')->where('slug', '[A-Za-z0-9_-]+');
    Route::get('download', 'HomeController@getDownload')->name('download');
    Route::redirect('home/download', '/download');

    Route::get('beatmapsets', 'OmsController@beatmaps')->name('beatmapsets.index');
    Route::get('beatmapsets/{beatmapset}', 'OmsController@beatmapset')->name('beatmapsets.show');
    Route::get('beatmaps', 'OmsController@beatmapset')->name('beatmaps.show');
    Route::get('beatmaps/{beatmapset}', 'OmsController@beatmapset');
    Route::get('search', 'OmsController@beatmaps')->name('search');
    Route::get('ir', 'OmsController@ir')->name('ir');

    Route::get('users', 'OmsController@profileLegacy');
    Route::get('users/{user}', 'OmsController@profile')->name('users.show')->where('user', '[1-9][0-9]*');
    Route::get('rankings', 'OmsController@rankings')->name('rankings');
    Route::get('account', 'OmsController@account')->name('account.edit');
    Route::get('help', 'OmsController@help')->name('help');
    Route::get('credits', 'OmsController@credits')->name('credits');

    Route::get('community', 'OmsController@community')->name('forum.forums.index');
    Route::get('community/new', 'OmsController@communityNew')->name('forum.topics.create');
    Route::get('community/{topic}', 'OmsController@topic')->name('forum.topics.show')->where('topic', '[1-9][0-9]*');
    Route::get('community/posts/{topic}', function (Request $request, string $topic) {
        $query = $request->getQueryString();

        return redirect()->to(route('forum.topics.show', ['topic' => $topic]).($query === null ? '' : '?'.$query));
    })->where('topic', '[1-9][0-9]*');
    Route::get('community/topic', function () {
        $id = request()->query('id');
        abort_unless(is_string($id) && preg_match('/^[1-9][0-9]*$/D', $id) === 1, 422, '帖子 ID 不符合约定。');

        $query = request()->query();
        unset($query['id']);
        $query = http_build_query($query, '', '&', PHP_QUERY_RFC3986);

        return redirect()->to(route('forum.topics.show', ['topic' => $id]).($query === '' ? '' : '?'.$query));
    });
});
