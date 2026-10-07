// Remove unreachable upstream views from the OMS fork; history stays in Git.
import { readdir, unlink, writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const viewRoot = path.resolve(root, 'resources/views');
const keep = new Set([
  'master.blade.php',
  'layout/header.blade.php', 'layout/metadata.blade.php', 'layout/footer.blade.php',
  'layout/_nav2.blade.php', 'layout/_header_mobile.blade.php', 'layout/_header_user.blade.php',
  'layout/_popup_user.blade.php', 'layout/_popup_login.blade.php', 'layout/_sticky_header.blade.php',
  'layout/header_mobile/nav.blade.php', 'layout/_page_header_v4.blade.php',
  'layout/_react_js.blade.php', 'layout/_global_variables.blade.php',
  'layout/_loading_overlay.blade.php', 'layout/popup-container.blade.php', 'layout/error.blade.php',
  'home/user.blade.php', 'home/_user_header_default.blade.php',
  'home/_user_news_post_preview.blade.php', 'home/_user_giant_button.blade.php',
  'home/download.blade.php', 'home/credits.blade.php',
  'news/index.blade.php', 'news/show.blade.php', 'beatmapsets/index.blade.php',
  'beatmapsets/show.blade.php', 'users/show.blade.php', 'rankings/index.blade.php',
  'account/edit.blade.php', 'wiki/show.blade.php',
  'oms/_page_data.blade.php', 'oms/_pagination.blade.php',
  'forum/forums/index.blade.php', 'forum/forums/_topic.blade.php',
  'forum/topics/show.blade.php', 'forum/topics/create.blade.php',
  'forum/topics/_post.blade.php', 'forum/topics/_post_edit_form.blade.php',
]);
const removed = [];
async function walk(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const target = path.resolve(directory, entry.name);
    if (!target.startsWith(viewRoot + path.sep) || entry.isSymbolicLink()) throw new Error('Unexpected view path');
    if (entry.isDirectory()) await walk(target);
    else if (entry.isFile()) {
      const relative = path.relative(viewRoot, target).split(path.sep).join('/');
      if (!keep.has(relative)) { await unlink(target); removed.push(relative); }
    }
  }
}
await walk(viewRoot);
await mkdir(path.join(root, 'artifacts'), { recursive: true });
await writeFile(path.join(root, 'artifacts/pruned-views.json'), JSON.stringify({ kept: [...keep], removed }, null, 2) + '\n');
console.log(JSON.stringify({ kept: keep.size, removed: removed.length }));
