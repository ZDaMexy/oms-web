<?php

// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

declare(strict_types=1);

namespace App\Libraries;

use Symfony\Component\HttpKernel\Exception\HttpException;

final class OmsApiException extends HttpException
{
    public function __construct(
        int $status,
        public readonly string $errorCode,
        string $message,
        array $headers = [],
    ) {
        parent::__construct($status, $message, null, $headers);
    }
}
