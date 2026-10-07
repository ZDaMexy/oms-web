// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import * as React from 'react';
import { Status } from 'oms/components';
import { Controller } from './controller';
import Cover from './cover';
import DetailStats from './detail-stats';

export default function Detail({ controller }: { controller: Controller }) {
  return <>
    {controller.user != null && <Cover user={controller.user} own={controller.own} />}
    {controller.section !== 'history' && <div className='profile-detail'>
      <Status error={controller.performance.error} ready={controller.performance.data != null} />
      {controller.performance.data != null && <DetailStats data={controller.performance.data} />}
    </div>}
  </>;
}
