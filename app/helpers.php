<?php

// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

use App\Libraries\LocaleMeta;
use Illuminate\Http\Request as HttpRequest;
use Illuminate\Support\HtmlString;

// Original presentation helpers retained without model, session or remote workers.

function array_reject_null(iterable $array): array
{
    $ret = [];
    foreach ($array as $item) {
        if ($item !== null) {
            $ret[] = $item;
        }
    }

    return $ret;
}

function array_search_null($value, $array)
{
    return null_if_false(array_search($value, $array, true));
}

function background_image($url): string
{
    return present($url)
        ? sprintf(' style="background-image:url(\'%s\');" ', e($url))
        : '';
}

function blade_safe($html): HtmlString
{
    return new HtmlString($html);
}

function class_modifiers_flat(array $modifiersArray): array
{
    $ret = [];

    foreach ($modifiersArray as $modifiers) {
        if (is_array($modifiers)) {
            // either "$modifier => boolean" or "$i => $modifier|null"
            foreach ($modifiers as $k => $v) {
                if (is_bool($v)) {
                    if ($v) {
                        $ret[] = $k;
                    }
                } elseif ($v !== null) {
                    $ret[] = $v;
                }
            }
        } elseif (is_string($modifiers)) {
            $ret[] = $modifiers;
        }
    }

    return $ret;
}

function class_with_modifiers(string $className, ...$modifiersArray): string
{
    $class = $className;

    foreach (class_modifiers_flat($modifiersArray) as $m) {
        $class .= " {$className}--{$m}";
    }

    return $class;
}

function css_var_2x(string $key, ?string $url): ?HtmlString
{
    if (!present($url)) {
        return null;
    }

    $url = e($url);
    $url2x = retinaify($url);

    return blade_safe("{$key}: url('{$url}'); {$key}-2x: url('{$url2x}');");
}

function current_locale_meta(): LocaleMeta
{
    return locale_meta(app()->getLocale());
}

function format_rank(?int $rank): string
{
    return $rank !== null ? '#'.i18n_number_format($rank) : '-';
}

function get_valid_locale($requestedLocale)
{
    if (in_array($requestedLocale, $GLOBALS['cfg']['app']['available_locales'], true)) {
        return $requestedLocale;
    }
}

function hsl_to_hex($h, $s, $l)
{
    $c = (1 - abs(2 * $l - 1)) * $s;
    $x = $c * (1 - abs(fmod($h / 60, 2) - 1));
    $m = $l - ($c / 2);

    [$r, $g, $b] = match (true) {
        $h < 60  => [$c, $x, 0],
        $h < 120 => [$x, $c, 0],
        $h < 180 => [0, $c, $x],
        $h < 240 => [0, $x, $c],
        $h < 300 => [$x, 0, $c],
        default  => [$c, 0, $x]
    };

    $r = round(($r + $m) * 255);
    $g = round(($g + $m) * 255);
    $b = round(($b + $m) * 255);

    return sprintf('#%02x%02x%02x', $r, $g, $b);
}

function html_entity_decode_better($string)
{
    // ENT_HTML5 to handle more named entities (&apos;, etc?).
    return html_entity_decode($string, ENT_QUOTES | ENT_HTML5, 'UTF-8');
}

function html_excerpt($body, $limit = 300)
{
    $body = html_entity_decode_better(replace_tags_with_spaces($body));

    return e(truncate($body, $limit));
}

function img2x(array $attributes)
{
    if (!present($attributes['src'] ?? null)) {
        return;
    }

    $src2x = retinaify($attributes['src']);
    $attributes['srcset'] = "{$attributes['src']} 1x, {$src2x} 1.5x";

    return tag('img', $attributes);
}

function locale_meta(string $locale): LocaleMeta
{
    return LocaleMeta::find($locale);
}

function trim_unicode(?string $value)
{
    return preg_replace('/(^\s+|\s+$)/u', '', $value ?? '');
}

function truncate(string $text, $limit = 100, $ellipsis = '...')
{
    if (mb_strlen($text) > $limit) {
        return mb_substr($text, 0, $limit - mb_strlen($ellipsis)).$ellipsis;
    }

    return $text;
}

function truncate_inclusive(string $text, int $limit): string
{
    if (mb_strlen($text) > $limit) {
        return mb_substr($text, 0, $limit).'...';
    }

    return $text;
}

function json_date(?DateTimeInterface $date): ?string
{
    return $date === null ? null : $date->format('Y-m-d');
}

function json_time(?DateTimeInterface $time): ?string
{
    return $time === null ? null : $time->format(DateTime::ATOM);
}

function osu_trans($key = null, $replace = [], $locale = null)
{
    $translator = app('translator');

    if (is_null($key)) {
        return $translator;
    }

    if (!trans_exists($key, $locale)) {
        $locale = $GLOBALS['cfg']['app']['fallback_locale'];
    }

    return $translator->get($key, $replace, $locale, false);
}

function osu_trans_choice($key, $number, array $replace = [], $locale = null)
{
    if (!trans_exists($key, $locale)) {
        $locale = $GLOBALS['cfg']['app']['fallback_locale'];
    }

    if (is_array($number) || $number instanceof Countable) {
        $number = count($number);
    }

    if (!isset($replace['count_delimited'])) {
        $replace['count_delimited'] = i18n_number_format($number, null, null, null, $locale);
    }

    return app('translator')->choice($key, $number, $replace, $locale);
}

function replace_tags_with_spaces($body)
{
    return preg_replace('#<[^>]+>#', ' ', $body);
}

function request_attribute_remember(string $key, callable $callback): mixed
{
    $request = Request::instance();
    $attributes = $request->attributes;

    $hasValue = $attributes->has($key);

    if ($hasValue) {
        $value = $attributes->get($key);
    } else {
        $value = $callback($request);
        $attributes->set($key, $value);
    }

    return $value;
}

function spinner(?array $modifiers = null)
{
    return tag('div', [
        'class' => class_with_modifiers('la-ball-clip-rotate', $modifiers),
    ]);
}

function tag($element, $attributes = [], $content = null)
{
    $attributeString = '';

    foreach ($attributes ?? [] as $key => $value) {
        $attributeString .= ' '.$key.'="'.e($value).'"';
    }

    return '<'.$element.$attributeString.'>'.($content ?? '').'</'.$element.'>';
}

function trans_exists($key, $locale)
{
    $translated = app('translator')->get($key, [], $locale, false);

    return present($translated) && $translated !== $key;
}

function ext_view($view, $data = null, $type = null, $status = null)
{
    static $types = [
        'atom' => 'application/atom+xml',
        'html' => 'text/html',
        'js' => 'application/javascript',
        'json' => 'application/json',
        'opensearch' => 'application/opensearchdescription+xml',
        'rss' => 'application/rss+xml',
    ];

    return response()->view(
        $view,
        $data ?? [],
        $status ?? 200,
        ['Content-Type' => $types[$type ?? 'html']]
    );
}

function is_http(string $url): bool
{
    return str_starts_with($url, 'http://')
        || str_starts_with($url, 'https://');
}

function is_turbo_request(?HttpRequest $request = null): bool
{
    $request ??= Request::instance();

    return $request->headers->get('x-turbo-request-id') !== null;
}

function timeago($date)
{
    $formatted = json_time($date);

    return "<time class='js-timeago' datetime='{$formatted}'>{$formatted}</time>";
}

function link_to(string $url, HtmlString|string $text, array $attributes = []): HtmlString
{
    return blade_safe(tag('a', [...$attributes, 'href' => $url], make_blade_safe($text)));
}

function make_blade_safe(HtmlString|string $text): HtmlString
{
    return $text instanceof HtmlString ? $text : blade_safe(e($text));
}

function presence($string, $valueIfBlank = null)
{
    return present($string) ? $string : $valueIfBlank;
}

function present($string)
{
    return $string !== null && $string !== '';
}

function user_color_style($color, $style)
{
    if (!present($color)) {
        return '';
    }

    return sprintf('%s: %s', $style, e($color));
}

function i18n_date(
    DateTimeInterface $datetime,
    int $format = IntlDateFormatter::LONG,
    ?string $transPattern = null,
    ?string $pattern = null,
) {
    $formatter = IntlDateFormatter::create(
        App::getLocale(),
        $format,
        IntlDateFormatter::NONE
    );

    if ($transPattern !== null) {
        $formatter->setPattern(osu_trans("common.datetime.{$transPattern}.php"));
    } elseif ($pattern !== null) {
        $formatter->setPattern($pattern);
    }

    return $formatter->format($datetime);
}

function i18n_date_auto(DateTimeInterface $date, string $skeleton): string
{
    $locale = App::getLocale();
    $generator = new IntlDatePatternGenerator($locale);
    $pattern = $generator->getBestPattern($skeleton);

    return IntlDateFormatter::formatObject($date, $pattern, $locale);
}

function i18n_number_format($number, $style = null, $pattern = null, $precision = null, $locale = null)
{
    if ($number === null) {
        return null;
    }

    if ($style === null && $pattern === null && $precision === null) {
        static $formatters = [];
        $locale ??= App::getLocale();
        $formatter = $formatters[$locale] ??= new NumberFormatter($locale, NumberFormatter::DEFAULT_STYLE);
    } else {
        $formatter = new NumberFormatter(
            $locale ?? App::getLocale(),
            $style ?? NumberFormatter::DEFAULT_STYLE,
            $pattern
        );

        if ($precision !== null) {
            $formatter->setAttribute(NumberFormatter::FRACTION_DIGITS, $precision);
        }
    }

    return $formatter->format($number);
}

function get_arr($input, $callback = null)
{
    if (is_array($input)) {
        if ($callback === null) {
            return $input;
        }

        $result = [];
        foreach ($input as $value) {
            $casted = call_user_func($callback, $value);

            if ($casted !== null) {
                $result[] = $casted;
            }
        }

        return $result;
    }
}

function get_bool($string)
{
    if (is_bool($string)) {
        return $string;
    } elseif ($string === 1 || $string === '1' || $string === 'on' || $string === 'true') {
        return true;
    } elseif ($string === 0 || $string === '0' || $string === 'false') {
        return false;
    }
}

function get_float($string)
{
    if (present($string) && is_scalar($string)) {
        return (float) $string;
    }
}

function get_int($string)
{
    if (present($string) && is_scalar($string)) {
        return (int) $string;
    }
}

function get_string($input)
{
    if (is_scalar($input)) {
        return (string) $input;
    }
}

function get_class_basename($className)
{
    return substr($className, strrpos($className, '\\') + 1);
}

function get_class_namespace($className)
{
    return substr($className, 0, strrpos($className, '\\'));
}

function null_if_false($value)
{
    return $value === false ? null : $value;
}

function retinaify($url)
{
    return preg_replace('/(\.[^.]+)$/', '@2x\1', $url);
}

function section_to_hue_map($section): int
{
    static $colourToHue = [
        'blue' => 200,
        'darkorange' => 20,
        'green' => 115,
        'orange' => 45,
        'pink' => 333,
        'purple' => 255,
        'red' => 0,
    ];

    static $sectionMapping = [
        'admin' => 'red',
        'beatmaps' => 'blue',
        'community' => 'pink',
        'error' => 'pink',
        'help' => 'orange',
        'home' => 'purple',
        'multiplayer' => 'pink',
        'rankings' => 'green',
        'store' => 'darkorange',
        'user' => 'pink',
    ];

    return $colourToHue[$sectionMapping[$section] ?? 'pink'];
}

function unmix(string $resource): HtmlString
{
    return app('assets-manifest')->src($resource);
}

function default_mode(): string
{
    return request()->query('ruleset', 'bms');
}

function page_title(): string
{
    return [
        'home' => '首页',
        'news-index' => '新闻',
        'news-show' => '新闻',
        'beatmaps' => '谱面',
        'beatmapset' => '谱面',
        'profile' => '个人页',
        'rankings' => '玩家榜',
        'community' => '社区',
        'topic' => '社区',
        'community-new' => '发布帖子',
        'download' => '下载',
        'help' => '帮助',
        'account' => '账号',
        'credits' => '源码与许可',
        'ir' => '谱面排行',
    ][request()->attributes->get('oms_page')] ?? 'OMS';
}

function nav_links(): array
{
    return [
        'home' => [
            '_' => route('home'),
            '首页' => route('home'),
            '新闻' => route('news.index'),
            '下载' => route('download'),
        ],
        'beatmaps' => [
            '_' => route('beatmapsets.index'),
            'BMS 谱面' => route('beatmapsets.index', ['ruleset' => 'bms']),
            'mania 谱面' => route('beatmapsets.index', ['ruleset' => 'mania']),
        ],
        'rankings' => [
            '_' => route('rankings'),
            '玩家榜' => route('rankings'),
            '谱面榜' => route('ir'),
        ],
        'community' => [
            '_' => route('forum.forums.index'),
            '帖子' => route('forum.forums.index'),
            '发布帖子' => route('forum.topics.create'),
        ],
        'help' => [
            '_' => route('help'),
            '入门帮助' => route('help'),
            '源码与许可' => route('credits'),
        ],
    ];
}

function footer_legal_links(): array
{
    return [
        'source_code' => config('oms.source_url'),
        'credits' => route('credits'),
    ];
}

function footer_landing_links(): array
{
    return [
        'general' => [
            'home' => route('home'),
            'beatmaps' => route('beatmapsets.index'),
            'download' => route('download'),
        ],
        'help' => [
            'faq' => route('help'),
            'forum' => route('forum.forums.index'),
        ],
        'legal' => footer_legal_links(),
    ];
}

function osu_url(string $key): ?string
{
    return config('osu.urls.'.$key);
}

function is_api_request(): bool
{
    $path = request()->getPathInfo();

    return str_starts_with($path, '/api/ir/') || str_starts_with($path, '/ir/adapters/');
}

function is_json_request(): bool
{
    return is_api_request() || request()->expectsJson();
}
