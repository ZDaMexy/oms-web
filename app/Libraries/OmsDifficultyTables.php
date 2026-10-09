<?php

declare(strict_types=1);

namespace App\Libraries;

class OmsDifficultyTables
{
    private ?array $manifest = null;

    public function listing(): array
    {
        $this->manifest ??= $this->read('manifest');

        return $this->manifest;
    }

    public function table(string $id): array
    {
        foreach ($this->listing()['tables'] as $table) {
            if ($table['id'] === $id) {
                return $table;
            }
        }

        abort(404);
    }

    public function charts(array $context): array
    {
        $table = $this->table($context['table']);
        abort_unless($table['status'] === 'ok', 503);
        $query = trim($context['q'] ?? '');
        $initial = $context['initial'] ?? '';
        $page = (string) ($context['page'] ?? 1);
        abort_unless(mb_strlen($query) <= 200
            && preg_match('/^(?:|[A-Z]|0-9|#)$/D', $initial) === 1
            && preg_match('/^[1-9][0-9]{0,6}$/D', $page) === 1
            && (int) $page <= 1000000, 422);

        // Snapshots are sorted across the complete table before filtering or
        // paging. No score population, source eligibility or rank is inferred.
        $items = $this->read($table['id'])['items'];
        $levels = [];
        foreach ($items as $item) {
            $key = 'level:'.($item['level'] ?? '');
            $levels[$key] ??= ['value' => $item['level'], 'count' => 0];
            $levels[$key]['count']++;
        }
        $levels = array_values($levels);
        usort($levels, static function (array $a, array $b): int {
            if ($a['value'] === null || $b['value'] === null) {
                return ($a['value'] === null) <=> ($b['value'] === null);
            }
            if (is_numeric($a['value']) && is_numeric($b['value'])) {
                $comparison = (float) $a['value'] <=> (float) $b['value'];
                if ($comparison !== 0) {
                    return $comparison;
                }
            }

            return strnatcmp($a['value'], $b['value']);
        });
        $filterLevel = array_key_exists('level', $context);
        $level = ($context['level'] ?? '') === '' ? null : $context['level'];
        abort_unless(!$filterLevel || in_array($level, array_column($levels, 'value'), true), 422);
        $matches = [];
        $initials = [];
        foreach ($items as $item) {
            if ($filterLevel && $item['level'] !== $level) {
                continue;
            }
            if ($query !== '' && mb_stripos(($item['title'] ?? '').' '.($item['artist'] ?? '').' '.($item['md5'] ?? ''), $query) === false) {
                continue;
            }
            $initials[$item['initial']] = ($initials[$item['initial']] ?? 0) + 1;
            if ($initial === '' || $initial === $item['initial']) {
                $matches[] = $item;
            }
        }

        return [
            'table' => $table,
            'items' => array_slice($matches, ((int) $page - 1) * 50, 50),
            'page' => (int) $page,
            'limit' => 50,
            'total' => count($matches),
            'initial_counts' => $initials,
            'levels' => $levels,
        ];
    }

    public function chart(array $context): array
    {
        $metadata = $this->table($context['table']);
        abort_unless($metadata['status'] === 'ok', 503);
        foreach ($this->read($metadata['id'])['items'] as $item) {
            if ($item['md5'] === $context['md5']
                && (!array_key_exists('level', $context) || $item['level'] === ($context['level'] === '' ? null : $context['level']))) {
                return ['table' => $metadata, 'chart' => $item];
            }
        }

        abort(404);
    }

    private function read(string $name): array
    {
        return json_decode(file_get_contents(resource_path('oms/difficulty-tables/'.$name.'.json')), true, 512, JSON_THROW_ON_ERROR);
    }
}
