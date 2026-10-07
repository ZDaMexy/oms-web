<?php

return [
    'default' => 'daily',
    'channels' => [
        'daily' => [
            'driver' => 'daily',
            'path' => storage_path('logs/laravel.log'),
            'level' => 'warning',
            'days' => 7,
        ],
    ],
];
