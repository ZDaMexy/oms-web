<?php

// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

declare(strict_types=1);

namespace App\Libraries;

use GuzzleHttp\Client;
use GuzzleHttp\Exception\TransferException;
use Illuminate\Http\Request;
use InvalidArgumentException;
use JsonException;
use Psr\Http\Message\ResponseInterface;
use Symfony\Component\HttpFoundation\Response;

class OmsApi
{
    public const ADAPTER_FILES = [
        'omsir-beatoraja-0.8.8-0.1.0.jar',
        'omsir-lr2oraja-build11611350155-0.1.0.jar',
        'omsir-ed-v0.4.0-0.1.0.jar',
        'OmsIR-v260915.x64.dll',
        'OmsIR-v260915.x86.dll',
        'nlohmann-json-LICENSE.MIT.txt',
        'zlib-LICENSE.txt',
        'versions.json',
    ];

    private Client $client;

    public function __construct(string $baseUrl, private readonly Request $incomingRequest)
    {
        $parts = parse_url($baseUrl);
        if (!is_array($parts)
            || !in_array($parts['scheme'] ?? null, ['http', 'https'], true)
            || !isset($parts['host'])
            || isset($parts['user'])
            || isset($parts['pass'])
            || isset($parts['query'])
            || isset($parts['fragment'])
            || !in_array($parts['path'] ?? '', ['', '/'], true)
        ) {
            throw new InvalidArgumentException('OMS_API_BASE 必须是明确配置的 HTTP 服务地址，不含凭据、路径或查询。');
        }

        $this->client = new Client([
            'base_uri' => rtrim($baseUrl, '/').'/',
            'allow_redirects' => false,
            'connect_timeout' => 1,
            'timeout' => 26,
            'http_errors' => false,
            'proxy' => '',
            'cookies' => false,
            'decode_content' => false,
        ]);
    }

    public function getJson(string $path, array $query = []): array
    {
        $response = $this->request('GET', $path, $query, ['Accept' => 'application/json']);
        $status = $response->getStatusCode();

        try {
            $data = json_decode((string) $response->getBody(), true, 512, JSON_THROW_ON_ERROR);
        } catch (JsonException) {
            throw new OmsApiException(502, 'invalid_api_response', 'OMS 服务返回格式不符合约定。');
        }
        if (!is_array($data)) {
            throw new OmsApiException(502, 'invalid_api_response', 'OMS 服务返回格式不符合约定。');
        }
        if ($status < 200 || $status >= 300) {
            $error = $data['error'] ?? null;
            if (!is_array($error) || !is_string($error['code'] ?? null) || !is_string($error['message'] ?? null)) {
                throw new OmsApiException(502, 'invalid_api_response', 'OMS 服务返回了无效的错误响应。');
            }
            $headers = $response->hasHeader('Retry-After')
                ? ['Retry-After' => $response->getHeaderLine('Retry-After')]
                : [];

            throw new OmsApiException($status, $error['code'], $error['message'], $headers);
        }

        return $data;
    }

    public function adapter(Request $request): Response
    {
        $headers = [];
        foreach (['Accept', 'Accept-Encoding', 'Range', 'If-Range', 'If-None-Match', 'If-Modified-Since'] as $name) {
            if ($request->headers->has($name)) {
                $headers[$name] = $request->header($name);
            }
        }

        try {
            $upstream = $this->request(
                $request->getMethod(),
                $request->getPathInfo(),
                $request->getQueryString() ?? '',
                $headers,
            );
        } catch (OmsApiException $error) {
            $status = $error->getStatusCode();
            return new Response(
                json_encode(['error' => [
                    'code' => $error->errorCode,
                    'message' => $error->getMessage(),
                ]], JSON_UNESCAPED_UNICODE),
                $status,
                ['Content-Type' => 'application/json', 'Cache-Control' => 'no-store'],
            );
        }

        $response = new Response((string) $upstream->getBody(), $upstream->getStatusCode());
        $responseHeaders = [
            'Content-Type', 'Content-Encoding', 'Cache-Control', 'ETag', 'Last-Modified',
            'Retry-After', 'Vary', 'Location', 'Content-Disposition', 'Content-Length', 'Content-Range', 'Accept-Ranges',
        ];
        foreach ($responseHeaders as $name) {
            if ($upstream->hasHeader($name)) {
                $response->headers->set($name, $upstream->getHeader($name));
            }
        }

        return $response;
    }

    private function request(string $method, string $path, array|string $query, array $headers): ResponseInterface
    {
        // Only API paths and the published adapter files are accepted, never a
        // caller-provided URL or Host. Adapter downloads never carry identity.
        $isApi = preg_match('#^/api/ir/v[12]/[A-Za-z0-9._/-]+$#D', $path) === 1
            && !in_array('.', explode('/', $path), true)
            && !in_array('..', explode('/', $path), true);
        $isAdapter = str_starts_with($path, '/ir/adapters/')
            && in_array(substr($path, strlen('/ir/adapters/')), self::ADAPTER_FILES, true)
            && in_array($method, ['GET', 'HEAD'], true);
        if (!$isApi && !$isAdapter) {
            throw new OmsApiException(400, 'invalid_api_path', 'API 地址不符合约定。');
        }

        // FastCGI REMOTE_ADDR is set by our Nginx peer boundary. Never use an
        // incoming forwarding header, cookie or authorization for public SSR.
        $clientIp = $this->incomingRequest->server->get('REMOTE_ADDR');
        if (!is_string($clientIp) || filter_var($clientIp, FILTER_VALIDATE_IP) === false) {
            throw new InvalidArgumentException('OMS 页面请求缺少可信的客户端地址。');
        }
        $headers['X-Forwarded-For'] = $clientIp;

        try {
            return $this->client->request($method, ltrim($path, '/'), [
                'query' => $query,
                'headers' => $headers,
            ]);
        } catch (TransferException) {
            // Do not attach the transport exception: it can contain credentials.
            throw new OmsApiException(503, 'oms_service_unavailable', 'OMS 服务暂时无法连接，请稍后重试。');
        }
    }
}
