{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
<footer class="no-print {{ class_with_modifiers('footer', $modifiers ?? []) }}">
    <div class="footer__row">
        <a class="footer__link" href="/help">帮助</a>
        <a class="footer__link" href="/community">社区</a>
        <a class="footer__link" href="https://github.com/ZDaMexy/oms/issues">反馈</a>
        <a class="footer__link" href="/credits">源码与许可</a>
    </div>
    <div class="footer__row">OMS · BMS / mania</div>
    <div class="js-sync-height--target" data-sync-height-id="permanent-fixed-footer"></div>
</footer>