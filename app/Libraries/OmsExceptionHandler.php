<?php

// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

declare(strict_types=1);

namespace App\Libraries;

use Illuminate\Foundation\Exceptions\Handler;
use Symfony\Component\HttpKernel\Exception\HttpExceptionInterface;
use Throwable;

class OmsExceptionHandler extends Handler
{
    protected function context(): array
    {
        // PHP pages are anonymous; exception reporting must not resolve Auth.
        return [];
    }

    protected function renderExceptionResponse($request, Throwable $exception)
    {
        $status = $exception instanceof HttpExceptionInterface ? $exception->getStatusCode() : 500;
        $headers = $exception instanceof HttpExceptionInterface ? $exception->getHeaders() : [];
        $error = [
            'status' => $status,
            'code' => $exception instanceof OmsApiException ? $exception->errorCode : 'http_error',
            'message' => $exception instanceof OmsApiException ? $exception->getMessage() : match ($status) {
                400 => '请求地址不正确。',
                404 => '这个页面不存在。',
                405 => '这个入口不支持该操作。',
                422 => '筛选参数有误，请检查地址或重新选择筛选条件。',
                429 => '请求太频繁，请稍后重试。',
                503 => 'OMS 服务暂时不可用，请稍后重试。',
                default => '页面暂时无法打开，请稍后重试。',
            },
        ];
        $headers['Cache-Control'] = 'no-store';

        if (is_json_request()) {
            return response()->json(['error' => [
                'code' => $error['code'],
                'message' => $error['message'],
            ]], $status, $headers);
        }

        $request->attributes->set('oms_page', 'error');
        $request->attributes->set('route_section_error', [
            'namespace' => 'error',
            'controller' => 'oms',
            'action' => 'error',
            'section' => 'error',
        ]);

        return response()->view('layout.error', [
            'omsPage' => 'error',
            'omsData' => [],
            'omsError' => $error,
            'statusCode' => $status,
            'titleOverride' => '无法打开页面',
        ], $status, $headers);
    }
}
