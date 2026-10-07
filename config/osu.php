<?php

// Original presentation helpers still use this configuration namespace.
return [
    'is_development_deploy' => env('OMS_LOCAL_PREVIEW', true),
    'urls' => [
        'base' => rtrim(env('APP_URL', 'http://127.0.0.1:8080'), '/'),
        'source_code' => 'https://github.com/ZDaMexy/oms-web',
    ],
];
