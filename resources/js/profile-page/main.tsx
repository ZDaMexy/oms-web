// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import * as React from 'react';
import { Paginator, Status } from 'oms/components';
import useController from './controller';
import Detail from './detail';
import Header from './header';
import History from './history';
import PlayDetail from './play-detail';

export default function Main(_props: { container: HTMLElement }) {
  const controller = useController();
  const { records, query, update, section, performance } = controller;
  return <div className='osu-layout osu-layout--full'>
    <Header controller={controller} />
    <div className='osu-page osu-page--generic-compact'>
      <Status error={controller.profile.error} ready={controller.user != null} />
      {controller.user != null && <Detail controller={controller} />}
      <div className='sticky-toolbar'>
        <div className='page-mode page-mode--profile-page-extra'>
          <a className={'page-mode__item' + (section === 'best' ? ' page-mode__item--active' : '')}
            href='#top_ranks' onClick={event => { event.preventDefault(); update({ section: 'best', page: '1' }); }}>公开最佳</a>
          <a className={'page-mode__item' + (section === 'recent' ? ' page-mode__item--active' : '')}
            href='#recent_activity' onClick={event => { event.preventDefault(); update({ section: 'recent', page: '1' }); }}>近期最佳更新</a>
          {controller.own && <a className={'page-mode__item'+(section==='history'?' page-mode__item--active':'')}
            href='#history' onClick={event=>{event.preventDefault();update({section:'history',page:'1'});}}>我的完整记录</a>}
        </div>
      </div>
      {controller.user != null && <div className='user-profile-pages'>
        {section==='history' ? (controller.own ? <History controller={controller}/> : <section className='page-extra'><p>完整记录仅本人登录后可查看。</p></section>) : <section className='page-extra' id={section === 'best' ? 'top_ranks' : 'recent_activity'}>
          <h2 className='title title--page-extra'>{section === 'best' ? '公开最佳成绩' : '近期最佳更新'}</h2>
          <label className='score-condition-filter'>条件
            <select value={query.get('condition') ?? ''} onChange={event => update({ condition: event.target.value || null })}>
              <option value=''>所选来源的全部条件</option>
              {performance.data?.lanes.map(lane => <option key={lane.condition_scope.id} value={lane.condition_scope.id}>{lane.condition_scope.label}</option>)}
            </select>
          </label>
          {section === 'recent' && <p className='beatmapset-scoreboard__notice'>按网站收到最佳成绩的时间排列。这里只显示最佳成绩的更新；每次 OMS 游玩的记录在本人登录后的“我的完整记录”中查看。</p>}
          <Status error={records.error} ready={records.data != null} />
          {records.data != null && <>
            <p>{records.data.total.toLocaleString('zh-CN')} 条公开最佳</p>
            <div className='play-detail-list'>{records.data.items.map(item =>
              <PlayDetail key={item.score.record_id + ':' + item.condition_scope.id} item={item} />)}</div>
            {records.data.items.length === 0 && <p>{records.data.total === 0 ? '这个范围还没有公开成绩。' : '本页没有成绩，请返回第一页。'}</p>}
            <Paginator {...records.data} onPage={page => update({ page: String(page) }, false)} />
          </>}
        </section>}
      </div>}
    </div>
  </div>;
}
