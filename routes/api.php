<?php

// API traffic goes directly to the fixed OMS service in Nginx.
// PHP only delivers the eight approved adapters, without identity.

use App\Libraries\OmsApi;
use Illuminate\Support\Facades\Route;

Route::get('ir/adapters/{file}', 'OmsController@adapter')
    ->where('file', implode('|', array_map(static fn (string $file): string => preg_quote($file), OmsApi::ADAPTER_FILES)))
    ->name('oms.adapters');
