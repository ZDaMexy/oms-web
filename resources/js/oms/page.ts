import { useEffect, useState } from 'react';
import { Ruleset } from './types';

export function pageData<T>() {
  const element = (window.newBody ?? document.body).querySelector('#json-oms-page');
  if (element == null) throw new Error('缺少 OMS 页面数据。');
  return JSON.parse(element.textContent ?? '') as { page: string; data: T };
}
export function useQuery() {
  const [query, setQuery] = useState(new URLSearchParams((window.newUrl ?? location).search));
  useEffect(() => {
    const changed = () => setQuery(new URLSearchParams(location.search));
    window.addEventListener('popstate', changed);
    window.addEventListener('oms:query', changed);
    return () => { window.removeEventListener('popstate', changed); window.removeEventListener('oms:query', changed); };
  }, []);
  const update = (changes: Record<string, string | null>, reset = true) => {
    const next = new URLSearchParams(location.search);
    for (const [name, value] of Object.entries(changes)) {
      if (value == null) next.delete(name); else next.set(name, value);
    }
    if (reset && !('page' in changes)) next.set('page', '1');
    history.pushState(history.state, '', `${location.pathname}?${next}${location.hash}`);
    window.dispatchEvent(new Event('oms:query'));
  };
  return [query, update] as const;
}
export function ruleset(query: URLSearchParams): Ruleset { return query.get('ruleset') === 'mania' ? 'mania' : 'bms'; }
export function chartUrl(md5: string, mode: Ruleset, extras: Record<string, string> = {}) {
  return '/beatmaps?' + new URLSearchParams({ ruleset: mode, md5, ...extras });
}
export function keys(mode: Ruleset) {
  return mode === 'bms' ? ['bms_5k', 'bms_7k', 'bms_9k', 'pms_9k', 'bms_14k'] : Array.from({ length: 18 }, (_, i) => `mania_${i + 1}k`);
}
export const sourceNames: Record<string, string> = { oms: 'OMS', beatoraja: 'beatoraja', lr2oraja: 'LR2oraja', lr2oraja_ed: 'Endless Dream', openlr2: 'OpenLR2', 'lr2ir.v3.lr2': 'LR2IR 历史 · LR2', 'lr2ir.v3.sbmp': 'LR2IR 历史 · SBMP', 'lr2ir.v3.unknown': 'LR2IR 历史 · 未知客户端', ginger: 'Ginger Rush', '616': '616', sayobot: 'Sayobot' };
