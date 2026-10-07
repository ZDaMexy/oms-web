// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import * as React from 'react';
import { User } from 'oms/types';

export default function Cover({ user, own }: { user: User; own: boolean }) {
  return <div className='profile-info'>
    <div className='profile-info__details'>
      <div className='profile-info__info'>
        <h1 className='profile-info__name'><span className='u-ellipsis-pre-overflow'>{user.username}</span></h1>
        <div className='profile-info__title'>OMS · #{user.id}</div>
      </div>
      {own && <div className='profile-info__icons'><a className='btn-osu-big' href='/account'>账号与交分密钥</a></div>}
    </div>
  </div>;
}
