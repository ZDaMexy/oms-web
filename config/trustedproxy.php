<?php

use Illuminate\Http\Request;

return [
    'proxies' => array_values(array_filter(explode(',', env('TRUSTED_PROXIES', '')))),
    'headers' => Request::HEADER_X_FORWARDED_FOR | Request::HEADER_X_FORWARDED_HOST
        | Request::HEADER_X_FORWARDED_PORT | Request::HEADER_X_FORWARDED_PROTO,
];
