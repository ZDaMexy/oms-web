<?php

// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Libraries\OmsApi;
use App\Libraries\OmsDifficultyTables;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Routing\Controller;
use Illuminate\View\View;
use Symfony\Component\HttpFoundation\Response;

class OmsController extends Controller
{
    public function __construct(protected OmsApi $api, protected OmsDifficultyTables $difficultyTables)
    {
    }

    public function adapter(Request $request): Response
    {
        return $this->api->adapter($request);
    }

    public function beatmaps(Request $request): View
    {
        $context = $this->queryInput($request, [
            'ruleset' => 'bms', 'q' => '', 'page' => 1, 'cursor' => 0,
        ], ['ruleset', 'source', 'q', 'page', 'cursor', 'keys']);
        $context['source'] ??= $context['ruleset'] === 'mania' ? 'sayobot' : 'ginger';

        return $this->page('beatmapsets.index', 'beatmaps', [
            'context' => $context,
        ]);
    }

    public function beatmapset(Request $request, ?string $beatmapset = null): View
    {
        $context = $this->queryInput($request, [], ['ruleset', 'md5', 'sha256', 'sid', 'keys']);
        if (!isset($context['ruleset'])) {
            $routeHasMd5 = $beatmapset !== null && preg_match('/^[0-9a-fA-F]{32}$/D', $beatmapset) === 1;
            $context['ruleset'] = !isset($context['md5']) && !$routeHasMd5
                && (isset($context['sid']) || ($beatmapset !== null && ctype_digit($beatmapset))) ? 'mania' : 'bms';
        }

        if ($context['ruleset'] === 'mania') {
            if (isset($context['md5'])) {
                abort_unless(preg_match('/^[0-9a-fA-F]{32}$/D', $context['md5']) === 1, 422, '谱面 MD5 不符合约定。');
                $context['md5'] = strtolower($context['md5']);

                return $this->page('beatmapsets.show', 'beatmapset', ['context' => $context]);
            }
            $sid = $context['sid'] ?? $beatmapset;
            abort_unless(is_string($sid) && preg_match('/^[1-9][0-9]*$/D', $sid) === 1, 422, '请提供实际 mania 谱面集 ID。');
            $catalog = $this->api->getJson('/api/ir/v1/catalog/mania/sets/'.$sid, array_intersect_key($context, ['keys' => true]));
            $context['sid'] = $catalog['set']['sid'];
        } else {
            abort_unless($context['ruleset'] === 'bms', 422, '请选择 BMS 或 mania。');
            $md5 = $context['md5'] ?? $beatmapset;
            abort_unless(is_string($md5) && preg_match('/^[0-9a-fA-F]{32}$/D', $md5) === 1, 422, '请提供实际 BMS 谱面 MD5。');
            $context['md5'] = strtolower($md5);

            // Catalog absence or an unavailable source must not block a known
            // chart's scores. The browser reads metadata and scores separately.
            return $this->page('beatmapsets.show', 'beatmapset', ['context' => $context]);
        }

        return $this->page('beatmapsets.show', 'beatmapset', ['context' => $context, 'catalog' => $catalog]);
    }

    public function profile(Request $request, string $user): View
    {
        abort_unless(preg_match('/^[1-9][0-9]{0,18}$/D', $user) === 1
            && (strlen($user) < 19 || strcmp($user, '9223372036854775807') <= 0), 422, '账号 ID 不符合约定。');
        $context = $this->scopeInput($request);
        $context['id'] = $user;

        // A new account can see its own profile with its browser cookie while
        // remaining unavailable publicly. PHP must not make that auth decision.
        return $this->page('users.show', 'profile', ['context' => $context]);
    }

    public function profileLegacy(Request $request)
    {
        $query = $this->queryInput($request, [], ['id']);
        if (!isset($query['id'])) {
            return redirect()->route('account.edit');
        }
        return $this->profile($request, $query['id']);
    }

    public function rankings(Request $request): View
    {
        $context = $this->scopeInput($request);
        $context = $this->queryInput($request, [
            ...$context,
            'source' => 'oms',
            'metric' => $context['ruleset'] === 'mania' ? 'best_total_score' : 'coverage',
            'page' => 1,
            'limit' => 20,
        ], ['ruleset', 'keymode', 'source', 'metric', 'condition', 'page', 'limit']);
        unset($context['sources']);
        if (($context['condition'] ?? null) === '') {
            unset($context['condition']);
        }
        $scopeQuery = $this->queryInput($request, [
            'ruleset' => $context['ruleset'],
            'keymode' => $context['keymode'],
            'source' => $context['source'],
            'page' => 1,
            'limit' => 20,
        ], ['scope_page']);
        if (isset($scopeQuery['scope_page'])) {
            $scopeQuery['page'] = $scopeQuery['scope_page'];
            unset($scopeQuery['scope_page']);
        }
        $scopes = $this->api->getJson('/api/ir/v1/rankings/scopes', $scopeQuery);
        $needsCondition = $context['metric'] === 'cleared_charts' && !isset($context['condition']);

        return $this->page('rankings.index', 'rankings', [
            'context' => $context,
            'ranking' => $needsCondition ? null : $this->api->getJson('/api/ir/v1/rankings/players', $context),
            'scopes' => $scopes,
            'needsCondition' => $needsCondition,
        ]);
    }

    public function community(Request $request): View
    {
        $context = $this->queryInput($request, ['q' => '', 'page' => 1, 'limit' => 20], [
            'q', 'category', 'author_id', 'page', 'limit',
        ]);
        if (($context['category'] ?? null) === '') {
            unset($context['category']);
        }

        return $this->page('forum.forums.index', 'community', [
            'context' => $context,
            'posts' => $this->api->getJson('/api/ir/v1/community/posts', $context),
        ]);
    }

    public function topic(Request $request, string $topic): View
    {
        $post = $this->api->getJson('/api/ir/v1/community/posts/'.$topic);
        $query = $this->queryInput($request, ['page' => 1, 'limit' => 20], ['page', 'limit', 'reply_page']);
        if (isset($query['reply_page'])) {
            if (!$request->query->has('page')) {
                $query['page'] = $query['reply_page'];
            }
            unset($query['reply_page']);
        }

        return $this->page('forum.topics.show', 'topic', [
            'context' => ['id' => $topic, ...$query],
            'post' => $post,
            'replies' => $this->api->getJson('/api/ir/v1/community/posts/'.$topic.'/replies', $query),
        ]);
    }

    public function communityNew(): View
    {
        return $this->page('forum.topics.create', 'community-new');
    }

    public function ir(Request $request): View
    {
        $context = $this->queryInput($request, ['q' => '', 'page' => 1, 'limit' => 20], [
            'q', 'page', 'limit', 'md5', 'sources', 'mode', 'condition', 'table', 'initial', 'level',
        ]);
        if (isset($context['md5'])) {
            abort_unless(preg_match('/^[0-9a-fA-F]{32}$/D', $context['md5']) === 1, 422, '谱面 MD5 不符合约定。');
            $context['md5'] = strtolower($context['md5']);
            $context['ruleset'] = 'bms';
            $context['ir_only'] = true;
            if (isset($context['table'])) {
                $selected = $this->difficultyTables->chart($context);

                return $this->page('beatmapsets.show', 'beatmapset', [
                    'context' => $context,
                    'table_chart' => $selected['chart'],
                    'difficulty_table' => $selected['table'],
                ]);
            }
            return $this->page('beatmapsets.show', 'beatmapset', [
                'context' => $context,
                'chart' => $this->api->getJson('/api/ir/v2/charts/'.$context['md5']),
            ]);
        }

        return $this->page('beatmapsets.index', 'ir', [
            'context' => $context,
            'difficulty_tables' => $this->difficultyTables->listing(),
            'table_list' => isset($context['table']) ? $this->difficultyTables->charts($context) : null,
        ]);
    }

    public function difficultyTable(Request $request, string $table): JsonResponse
    {
        $context = $this->queryInput($request, ['q' => '', 'page' => 1, 'initial' => ''], ['q', 'page', 'initial', 'level']);
        $context['table'] = $table;

        return response()->json($this->difficultyTables->charts($context), 200, ['Cache-Control' => 'no-store']);
    }

    public function account(): View
    {
        return $this->page('account.edit', 'account');
    }

    public function help(): View
    {
        return $this->page('wiki.show', 'help');
    }

    public function credits(): View
    {
        return $this->page('home.credits', 'credits');
    }

    protected function page(string $view, string $page, array $data = [], array $extra = []): View
    {
        $request = request();
        $request->attributes->set('oms_page', $page);
        $request->attributes->set('route_section', [
            'namespace' => 'main',
            'controller' => snake_case(class_basename(static::class)),
            'action' => snake_case($request->route()->getActionMethod()),
            'section' => [
                'beatmaps' => 'beatmaps', 'beatmapset' => 'beatmaps',
                'profile' => 'user', 'rankings' => 'rankings', 'ir' => 'rankings',
                'community' => 'community', 'topic' => 'community', 'community-new' => 'community',
                'help' => 'help', 'account' => 'home',
            ][$page] ?? 'home',
        ]);

        return view($view, ['omsPage' => $page, 'omsData' => $data, ...$extra]);
    }

    protected function queryInput(Request $request, array $defaults, array $names): array
    {
        $values = $request->query();
        foreach ($names as $name) {
            if (array_key_exists($name, $values)) {
                abort_unless(is_string($values[$name]), 422, '查询字段必须是单个文本值。');
                // Keep an explicitly empty sources value: it means no source.
                $defaults[$name] = $values[$name];
            }
        }

        return $defaults;
    }

    private function scopeInput(Request $request): array
    {
        $context = $this->queryInput($request, ['ruleset' => 'bms'], ['ruleset', 'keymode', 'sources']);
        $context['keymode'] ??= $context['ruleset'] === 'mania' ? 'mania_7k' : 'bms_7k';

        return $context;
    }
}
