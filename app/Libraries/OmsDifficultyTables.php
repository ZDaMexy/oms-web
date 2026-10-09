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
        $matches = [];
        $initials = [];
        foreach ($items as $item) {
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
        ];
    }

    public function chart(string $table, string $md5): array
    {
        $metadata = $this->table($table);
        abort_unless($metadata['status'] === 'ok', 503);
        foreach ($this->read($metadata['id'])['items'] as $item) {
            if ($item['md5'] === $md5) {
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
