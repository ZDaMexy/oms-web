import { Main } from 'beatmaps/main';
import core from 'osu-core-singleton';
import * as React from 'react';
core.reactTurbolinks.register('beatmaps',()=> <Main/>);
