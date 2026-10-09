// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import HeaderV4 from 'components/header-v4';
import { ModeFilters, Sources } from 'oms/components';
import * as React from 'react';
import { Controller } from './controller';

export default function Header({ controller }: { controller: Controller }) {
  const { mode, keymode, query, update, id } = controller;
  return <HeaderV4 theme='users' links={[
    { title: '个人', url: '/users/' + id, active: true },
    { title: '帖子', url: '/community?author_id=' + id },
    { title: '玩家榜', url: '/rankings?' + new URLSearchParams({ ruleset: mode, keymode }) },
  ]} contentAppend={controller.section==='history'?undefined:<div className='beatmapsets-search__filters oms-profile-filters'>
    <ModeFilters mode={mode} keymode={keymode} onChange={changes => update(changes)} />
    <Sources mode={mode} live value={query.get('sources')} onChange={sources => update({ sources, condition: null })} />
  </div>} />;
}
