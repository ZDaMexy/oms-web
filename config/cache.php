<?php

return [
    'default' => 'file',
    'stores' => [
        'array' => ['driver' => 'array', 'serialize' => false],
        'file' => ['driver' => 'file', 'path' => storage_path('framework/cache')],
    ],
    'prefix' => 'oms-web',
];
