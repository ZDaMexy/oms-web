// OMS HTTP boundary types; no ppy user/statistics objects are synthesized.
export type Ruleset = 'bms' | 'mania';
export interface User { id: number; username: string }
export interface Page<T> { items: T[]; page: number; limit: number; total: number }
export interface DifficultyTable {
  id: string; name: string; symbol: string; count: number | null; status: 'ok' | 'unavailable';
  url: string; source_url: string | null;
}
export interface DifficultyTableChart {
  row: number; md5: string | null; title: string | null; artist: string | null; level: string | null; initial: string;
}
export interface Condition { id: string; label: string; comparison: string; conditions: Record<string, unknown>; unknown_fields: string[] }
export interface Lamp { family: string; value: number | string; label: string; source?: string; record_id?: string | null; rule_label?: string }
export interface Chart {
  md5: string | null; sha256: string | null; title: string | null; artist: string | null; difficulty: string | null;
  keymode: string | null; keys: number | null; bpm: number | null; notes: number | null;
  length_seconds: number | null; star_rating: number | null; bid: number | null;
}
export interface IrChart {
  chart: Pick<Chart, 'md5' | 'sha256' | 'title' | 'artist' | 'difficulty'> & { md5: string };
  ruleset: Ruleset;
  groups: { id: string; label: string }[];
  available_sources: string[];
  content_identity: string;
  archive_suspended: boolean;
}
export interface Package { id: string; name: string; size_bytes: number | null; download_url: string | null }
export interface CatalogSet {
  id: string; source: string; kind: 'bms-package' | 'mania-set'; title: string; artist: string | null; creator: string | null;
  cover_url: string | null; package: Package | null; charts: Chart[]; sid: number | null; detail_url: string; source_url: string | null;
}
export interface SourceStatus { source: string; status: string; message: string | null }
export interface CatalogSearch {
  ruleset: Ruleset; source: string; query: string; items: CatalogSet[]; page: number; limit: number;
  total: number | null; total_basis: string; next_cursor: number | null; has_more: boolean; source_status: SourceStatus[];
}
export interface Candidate {
  source: string; package: Package; chart: Chart; charts: Chart[]; cover_url: string | null; source_url: string | null;
  identity: string; eligible: boolean; availability: string; reason: string | null;
}
export interface BmsDetail { ruleset: 'bms'; chart: Chart | null; candidates: Candidate[]; recommended_source: string | null; source_status: SourceStatus[] }
export interface ManiaDetail { ruleset: 'mania'; set: CatalogSet; mixed_modes: boolean; download: { full_url: string; novideo_url: string }; source_status: SourceStatus[] }
export interface Source { code: string; label: string; available: boolean; record_kind: string; verification: string }
export interface PublicBest {
  chart: Pick<Chart, 'md5' | 'sha256' | 'title' | 'artist' | 'difficulty'>;
  ruleset: Ruleset; condition_scope: Condition;
  score: {
    record_id: string; record_kind: 'play' | 'best_state'; source: string;
    ex_score: number | null; max_ex_score: number | null; total_score: number | null;
    total_score_version: number | null; accuracy: number | null; passed: boolean | null;
    played_at: string | null; received_at: string; conditions: Record<string, unknown>; unknown_fields: string[]; lamp: Lamp | null;
  };
  best_lamps: Lamp[];
  activity?: { kind: string; order_at: string; played_at: string | null };
}
export interface OmsPlay {
  id: number; user_id: number; submission_id: string; schema_version: number; ruleset: Ruleset;
  chart: { md5: string; sha256: string; title: string; artist: string; difficulty: string };
  keymode: string; played_at: string; received_at: string; client_version: string;
  total_score: number; total_score_version: number; accuracy: number; max_combo: number; passed: boolean;
  ex_score: number|null; max_ex_score: number|null;
  statistics: Record<string,number>; maximum_statistics: Record<string,number>;
  mods: { acronym: string; settings: Record<string,unknown> }[];
  ruleset_data: ({ version: number; clear_lamp: number } & Record<string,unknown>)|null;
  bms_chart: Record<string,unknown>|null;
  group_id: string; group_label: string; trust: string; public_board: boolean;
}
export interface Performance {
  user: User; totals: { public_chart_count: number; public_best_count: number };
  lanes: { source: string; condition_scope: Condition;
    metrics: { public_chart_count: number; public_best_count: number; cleared_chart_count: number | null; best_total_score: string | null };
    rankings: { metric: string; rank: number | null; total_players: number }[];
  }[];
}
export interface BoardRow {
  rank: number; identity: { namespace: string; id: string; username: string };
  score: { record_id: string; record_kind: string; source: string; ex_score: number | null; max_ex_score: number | null; total_score?: number | null; played_at: string | null; received_at?: string | null; conditions: Record<string, unknown>; unknown_fields: string[]; lamp?: Lamp | null };
  best_lamps: Lamp[];
}
export interface Board extends Page<BoardRow> {
  me: BoardRow | null; selected_sources: string[]; conditions: {id: string; label: string}[]; notice: string;
}
export interface RankingRow { rank: number; user: User; value: string; public_chart_count: number; public_best_count: number }
export interface Ranking extends Page<RankingRow> { me: RankingRow | null }
