// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import * as React from 'react';
import { ModeFilters, Sources, Status } from 'oms/components';
import { Controller } from './controller';
import Cover from './cover';
import DetailStats from './detail-stats';

export default function Detail({ controller }: { controller: Controller }) {
  const { mode, keymode, query, update } = controller;
  return <>
    {controller.user != null && <Cover user={controller.user} own={controller.own} />}
    {controller.section !== 'history' && <div className='profile-detail'>
      <div className='profile-detail__filters'>
        <ModeFilters mode={mode} keymode={keymode} onChange={update} />
        <Sources mode={mode} live value={query.get('sources')} onChange={sources => update({ sources, condition: null })} />
      </div>
      <Status error={controller.performance.error} ready={controller.performance.data != null} />
      {controller.performance.data != null && <DetailStats data={controller.performance.data} />}
    </div>}
  </>;
}
