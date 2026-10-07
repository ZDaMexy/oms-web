// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import 'app-deps';
import 'jquery-pubsub.coffee';
import '_classes/timeout.coffee';
import 'osu-core-singleton';
import 'main.coffee';
import 'register-components';
import { session } from 'oms/api';
import 'oms/forms';

document.addEventListener('turbo:load', () => { void session.refresh(); });
