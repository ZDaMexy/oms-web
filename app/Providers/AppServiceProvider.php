<?php

// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

namespace App\Providers;

use App\Libraries\OmsApi;
use App\Libraries\OsuMessageSelector;
use App\Singletons\AssetsManifest;
use App\Singletons\RouteSection;
use Illuminate\Http\Request;
use Illuminate\Support\ServiceProvider;
use Illuminate\Support\Facades\View;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->app->singleton('assets-manifest', AssetsManifest::class);
        $this->app->singleton('route-section', RouteSection::class);
        $this->app->singleton(OmsApi::class, fn () => new OmsApi(config('oms.api_base')));
    }

    public function boot(): void
    {
        $GLOBALS['cfg'] = config()->all();
        $this->app->make('translator')->setSelector(new OsuMessageSelector());
        app('url')->forceScheme(parse_url(config('app.url'), PHP_URL_SCHEME));
        Request::setTrustedProxies(config('trustedproxy.proxies'), config('trustedproxy.headers'));

        View::composer('*', function ($view): void {
            $view->with([
                'currentUser' => null,
                'navLinks' => nav_links(),
                'currentLocaleMeta' => current_locale_meta(),
            ]);
        });
    }
}
