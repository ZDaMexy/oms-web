import type { BoardRow, ScoreMod } from './types';

export interface ScoreOption {
  code: string;
  label: string;
  family: 'layout' | 'gauge' | 'rule' | 'assist' | 'visual' | 'unknown';
  icon: string;
  detail?: string;
}

const gauges: Record<string, string> = { AssistEasy: 'A-EASY', Easy: 'EASY', Normal: 'NORMAL', Hard: 'HARD', ExHard: 'EX-HARD', Hazard: 'HAZARD' };
const knownMods: Record<string, [string, ScoreOption['family'], string]> = {
  MR: ['镜像', 'layout', 'exchange-alt'], RD: ['随机', 'layout', 'random'],
  ASCR: ['自动皿', 'assist', 'compact-disc'], ANOT: ['自动键', 'assist', 'keyboard'], AT: ['全自动', 'assist', 'robot'],
  HID: ['Hidden', 'visual', 'eye-slash'], SUD: ['Sudden', 'visual', 'eye'], LIFT: ['Lift', 'visual', 'arrow-up'],
  OD: ['OMS 判定', 'rule', 'bullseye'], LR2: ['LR2 判定', 'rule', 'bullseye'], BRJ: ['beatoraja 判定', 'rule', 'bullseye'], IIDXJ: ['IIDX 判定', 'rule', 'bullseye'],
  LR2G: ['LR2 血条规则', 'rule', 'heartbeat'], BRG: ['beatoraja 血条规则', 'rule', 'heartbeat'], IIDXG: ['IIDX 血条规则', 'rule', 'heartbeat'],
  LN: ['标准 LN', 'rule', 'grip-lines-vertical'], CN: ['Charge Note', 'rule', 'grip-lines-vertical'], HCN: ['Hell Charge Note', 'rule', 'grip-lines-vertical'],
};

function gauge(label: string, original: string): ScoreOption {
  return { code: label, label: original, family: 'gauge', icon: 'heartbeat' };
}

function layout(mode: number, original: string, open: boolean, side?: string): ScoreOption {
  const names = open
    ? ['原谱', 'Mirror', 'Random', 'SRandom']
    : ['原谱', 'Mirror', 'Random', 'RRandom', 'SRandom', 'Spiral', 'HRandom', 'All Scratch', 'Random EX', 'SRandom EX'];
  const modeName = names[mode];
  const codes: Record<string, string> = { '原谱': 'NM', Mirror: 'MR', Random: 'RD', RRandom: 'R-RD', SRandom: 'S-RD' };
  return {
    code: codes[modeName] ?? modeName ?? String(mode),
    label: original + ' · ' + (modeName ?? '未识别选项'), family: 'layout',
    icon: mode === 0 ? 'minus' : mode === 1 ? 'exchange-alt' : 'random', detail: side,
  };
}

export function omsOptions(mods: ScoreMod[], conditions?: Record<string, unknown>): ScoreOption[] {
  const options: ScoreOption[] = [];
  if (conditions?.gauge_auto_shift === true) {
    options.push({ code: 'GAS', label: '自动降档 · ' + conditions.starting_gauge_type + ' → ' + conditions.floor_gauge_type, family: 'gauge', icon: 'level-down-alt' });
  } else if (typeof conditions?.starting_gauge_type === 'string') {
    const value = conditions.starting_gauge_type;
    options.push(gauge(gauges[value] ?? value, 'OMS · 起始血条 ' + value));
  }
  for (const mod of mods) {
    if (mod.acronym === 'GAS' || ['A-EASY', 'EASY', 'HARD', 'EX-HARD', 'HAZARD'].includes(mod.acronym)) continue;
    const known = knownMods[mod.acronym];
    const mode = mod.settings.random_mode;
    const code = mod.acronym === 'RD' && mode === 'SRandom' ? 'S-RD' : mod.acronym === 'RD' && mode === 'RRandom' ? 'R-RD' : mod.acronym;
    options.push({ code, label: (known?.[0] ?? mod.acronym) + (Object.keys(mod.settings).length ? ' · ' + JSON.stringify(mod.settings) : ''), family: known?.[1] ?? 'unknown', icon: known?.[2] ?? 'sliders-h' });
  }
  if (!mods.some(mod => mod.acronym === 'MR' || mod.acronym === 'RD')) options.push(layout(0, 'OMS · 原谱', false));
  return options;
}

export function scoreOptions(score: BoardRow['score']): ScoreOption[] {
  if (score.source === 'oms') return omsOptions(score.mods ?? [], score.conditions);
  const c = score.conditions;
  if (score.record_kind === 'archive_best') {
    // OP column positions vary between archived layouts; recognise tokens only.
    const aliases: Record<string, ScoreOption> = {
      '難': gauge('HARD', 'HARD'), HARD: gauge('HARD', 'HARD'), '易': gauge('EASY', 'EASY'), EASY: gauge('EASY', 'EASY'),
      '普': gauge('NORMAL', 'NORMAL'), NORMAL: gauge('NORMAL', 'NORMAL'), '死': gauge('HAZARD', 'HAZARD'),
      '正': layout(0, '原谱', false), '乱': layout(2, 'Random', false), RAN: layout(2, 'Random', false),
      '鏡': layout(1, 'Mirror', false), MIR: layout(1, 'Mirror', false),
    };
    return ['option_1', 'option_2', 'option_3', 'option_4'].flatMap(key => {
      const raw = c[key];
      if (typeof raw !== 'string' || raw === '') return [];
      const alias = aliases[raw];
      return [{ ...(alias ?? { code: raw, family: 'unknown' as const, icon: 'sliders-h' }), label: '旧库 ' + key + ' = ' + raw + (alias ? ' · ' + alias.label : '') }];
    });
  }
  const open = score.source === 'openlr2';
  const options: ScoreOption[] = [];
  if (typeof c.gauge === 'number') {
    const labels = open
      ? ['NORMAL', 'HARD', 'HAZARD', 'EASY', 'P-ATTACK', 'G-ATTACK']
      : ['A-EASY', 'EASY', 'NORMAL', 'HARD', 'EX-HARD', 'HAZARD', 'CLASS', 'EX-CLASS', 'EX-HARD-CLASS'];
    options.push(gauge(c.gauge === -1 ? 'SHIFT' : labels[c.gauge] ?? 'G ' + c.gauge,
      score.source + ' · gauge=' + c.gauge + (open && c.gauge === 2 ? ' · DEATH' : c.gauge === -1 ? ' · 血条切换，未提供起点与底档' : '')));
  }
  const dp = c.keymode === 'bms_14k';
  if (open) {
    for (const [field, side] of [['random_p1', '1P'], ['random_p2', '2P']]) {
      if ((side === '1P' || dp) && typeof c[field] === 'number') options.push(layout(c[field] as number, 'OpenLR2 · ' + field + '=' + c[field], true, dp ? side : undefined));
    }
    if (dp && c.dpflip === 1) options.push({ code: 'FLIP', label: 'OpenLR2 · DP FLIP', family: 'layout', icon: 'arrows-alt-h' });
  } else if (typeof c.option === 'number') {
    const value = c.option;
    if (Number.isInteger(value) && value >= 0 && value < 200) {
      options.push(layout(value % 10, score.source + ' · option=' + value, false, dp ? '1P' : undefined));
      if (dp) options.push(layout(Math.floor(value / 10) % 10, score.source + ' · option=' + value, false, '2P'));
      if (dp && Math.floor(value / 100) === 1) options.push({ code: 'FLIP', label: score.source + ' · DP FLIP', family: 'layout', icon: 'arrows-alt-h' });
    } else options.push({ code: 'OP ' + value, label: '原生 option=' + value + '，未确认映射', family: 'unknown', icon: 'sliders-h' });
  }
  return options;
}
