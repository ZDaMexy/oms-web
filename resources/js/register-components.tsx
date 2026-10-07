// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import ClickToCopy from 'components/click-to-copy';
import core from 'osu-core-singleton';
import * as React from 'react';

core.reactTurbolinks.register('click-to-copy', container =>
  <ClickToCopy {...JSON.parse(container.dataset.props ?? '')} />);
