import { useApi } from 'oms/api';
import { Paginator, Status } from 'oms/components';
import { DifficultyTable, DifficultyTableChart, Page } from 'oms/types';
import * as React from 'react';

interface TablePage extends Page<DifficultyTableChart> {
  table: DifficultyTable;
  initial_counts: Record<string, number>;
  levels: { value: string | null; count: number }[];
}
export interface IrSearchData {
  context: { table?: string; level?: string; initial?: string; q?: string; page?: number | string };
  difficulty_tables: { index_url: string; fetched_at: string; tables: DifficultyTable[] };
  table_list: TablePage | null;
}
interface Props {
  query: URLSearchParams;
  update: (changes: Record<string, string | null>) => void;
  initial: IrSearchData;
}
const initials = ['0-9', ...'ABCDEFGHIJKLMNOPQRSTUVWXYZ', '#'];
const initialName = (letter: string) => letter === '#' ? '其他' : letter === '0-9' ? '数字' : letter;

export function IrSearchContent({ query, update, initial }: Props) {
  const table = query.get('table');
  const level = query.get('level');
  const letter = query.get('initial') ?? '';
  const q = query.get('q') ?? '';
  const page = query.get('page') ?? '1';
  const params = new URLSearchParams({ initial: letter, q, page });
  if (level != null) params.set('level', level);
  const sameScope = table === initial.context.table && letter === (initial.context.initial ?? '')
    && level === (initial.context.level ?? null) && q === (initial.context.q ?? '') && Number(page) === Number(initial.context.page ?? 1);
  const result = useApi<TablePage>(table == null ? null : '/ir/tables/' + encodeURIComponent(table) + '?' + params,
    sameScope ? initial.table_list ?? undefined : undefined, 'public');
  const [text, setText] = React.useState(q);
  React.useEffect(() => { setText(q); }, [q]);
  const selected = initial.difficulty_tables.tables.find(item => item.id === table);
  const levels = result.data?.levels ?? [];
  const chartUrl = (md5: string) => {
    const context = new URLSearchParams({ table: table!, md5 });
    if (level != null) context.set('level', level);
    return '/ir?' + context;
  };

  return <>
    <div className='osu-page osu-page--beatmapsets-search-header'>
      <div className='difficulty-tables__filters'>
        <label className='difficulty-tables__picker'>难度表
          <select aria-label='选择难度表' value={table ?? ''} onChange={event => update({ table: event.target.value || null, level: null, q: null, initial: null, page: '1' })}>
            <option value=''>请选择难度表（{initial.difficulty_tables.tables.length} 个）</option>
            {initial.difficulty_tables.tables.map(item => <option key={item.id} value={item.id}>{item.name}{item.status === 'ok' ? '' : '（暂不可用）'}</option>)}
          </select>
        </label>
        <label className='difficulty-tables__picker difficulty-tables__picker--level'>难度
          <select aria-label='选择表内难度' disabled={table == null || result.data == null} value={level == null ? '' : 'level:' + level}
            onChange={event => update({ level: event.target.value === '' ? null : event.target.value.slice(6), page: '1' })}>
            <option value=''>全部难度</option>
            {levels.map(option => <option key={option.value ?? ''} value={'level:' + (option.value ?? '')}>
              {option.value == null ? '未标注' : (selected?.symbol ?? '') + option.value}（{option.count.toLocaleString('zh-CN')} 项）
            </option>)}
          </select>
        </label>
        <form className='difficulty-tables__search' onSubmit={event => { event.preventDefault(); update({ q: text.trim(), page: '1' }); }}>
          <input aria-label='搜索表内曲目' type='search' maxLength={200} disabled={table == null} value={text} onChange={event => setText(event.target.value)} placeholder='在这张表中搜索曲名或作者'/>
          <button type='submit' disabled={table == null} aria-label='搜索表内曲目'><span className='fas fa-search'/></button>
        </form>
        <p className='difficulty-tables__source'>收录 <a href={initial.difficulty_tables.index_url} target='_blank' rel='noopener noreferrer'>Zris 镜像目录</a>的全部选项 · 数据 {initial.difficulty_tables.fetched_at.slice(0, 10)}</p>
      </div>
    </div>
    <div className='osu-page'>
      <div className='difficulty-tables'>
        {table == null ? <div className='difficulty-tables__empty'><span className='fas fa-list'/><h2>先选一张难度表</h2><p>选表后可筛选难度，再按曲名首字母排列。点击曲目查看成绩榜。</p></div> : <>
          {selected != null && <div className='difficulty-tables__heading'><h2>{selected.name}</h2><a href={selected.source_url ?? selected.url} target='_blank' rel='noopener noreferrer'>原表 <span className='fas fa-external-link-alt'/></a></div>}
          <nav className='difficulty-tables__initials' aria-label='按曲名首字母筛选'>
            {['', ...initials].map(value => <button type='button' key={value} aria-pressed={value === letter}
              disabled={value !== '' && result.data != null && (result.data.initial_counts[value] ?? 0) === 0}
              className={'difficulty-tables__initial' + (value === letter ? ' difficulty-tables__initial--active' : '')}
              onClick={() => update({ initial: value || null, page: '1' })}>{value === '' ? '全部' : initialName(value)}</button>)}
          </nav>
          <Status error={result.error} ready={result.data != null}/>
          {result.data != null && <>
            <p className='difficulty-tables__count'>{result.data.total.toLocaleString('zh-CN')} 项 · 按曲名排序{letter === '' ? '' : ' · ' + initialName(letter)}</p>
            <div className='difficulty-tables__rows'>
              {result.data.items.map((item, index) => <React.Fragment key={item.row}>
                {(index === 0 || item.initial !== result.data!.items[index - 1].initial) && <h3 className='difficulty-tables__letter'>{initialName(item.initial)}</h3>}
                <div className='difficulty-tables__row'>
                  <span className='difficulty-tables__level'>{item.level == null || item.level === '' ? '—' : result.data!.table.symbol + item.level}</span>
                  <div className='difficulty-tables__song'>
                    {item.md5 == null ? <span>{item.title ?? '曲名未提供'}</span> : <a href={chartUrl(item.md5)}>{item.title ?? '曲名未提供'}</a>}
                    {item.artist != null && <span className='difficulty-tables__artist'>{item.artist}</span>}
                  </div>
                  {item.md5 == null ? <a className='difficulty-tables__unavailable' href={result.data!.table.source_url ?? result.data!.table.url} target='_blank' rel='noopener noreferrer' title='这条记录没有有效的单曲 MD5，查看原表'>查看原表</a> : <a className='difficulty-tables__board' href={chartUrl(item.md5)} aria-label={'查看 ' + (item.title ?? '这张谱面') + ' 的成绩榜'}><span className='fas fa-list-ol'/><span>成绩榜</span></a>}
                </div>
              </React.Fragment>)}
            </div>
            {result.data.items.length === 0 && <p className='difficulty-tables__empty'>{result.data.total === 0 ? '没有匹配曲目，可以换个难度、首字母或关键词。' : '本页没有曲目，请返回第一页。'}</p>}
            <Paginator page={result.data.page} total={result.data.total} limit={result.data.limit} onPage={value => update({ page: String(value) })}/>
          </>}
        </>}
      </div>
    </div>
  </>;
}
