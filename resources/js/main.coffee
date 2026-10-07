# Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
# See the LICENCE file in the repository root for full licence text.

import Menu from 'core-legacy/menu'
import Nav2 from 'core-legacy/nav2'
import TooltipDefault from 'core-legacy/tooltip-default'
import { navigate } from 'utils/turbolinks'

window.menu ?= new Menu
window.tooltipDefault ?= new TooltipDefault
window.nav2 ?= new Nav2(osuCore.clickMenu)

$(document).on 'change', '.js-url-selector', (e) ->
  navigate e.target.value, (e.target.dataset.keepScroll == '1')

$(document).on 'keydown', (e) ->
  $.publish 'key:esc' if e.key == 'Escape'

$(document).on 'click', '.clickable-row', (e) ->
  return if e.target.closest('a,button,input,select,textarea')
  e.currentTarget.querySelector('.clickable-row-link')?.click()
