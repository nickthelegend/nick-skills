// Generic version of fetch-web.mjs / fetch-web-more.mjs for web AND mobile shots (Oct 30, 2026).
// Fetches the top N real shots (no ads, no boosted slots) of each Dribbble search as individual images,
// de-duplicated against every shot already listed in web-shots/INDEX.md and mobile-shots/INDEX.md, and
// appends one section per run to the right INDEX.md. Same Playwright + CDN + sips pipeline as fetch-web.mjs.
//
// Size: Dribbble shots are 4:3 and the CDN `?resize=WxH` never upscales (a 2048x1536 original asked for
// 2400x1800 comes back at 2048x1536), so asking for 1800x1350 and keeping only images that come back at
// exactly 1800x1350 keeps real >=1800px originals and drops small uploads, odd aspect ratios and placeholders.
// Mobile shots on Dribbble use the same 4:3 canvas (phones laid out on a board), so both kinds use 1800x1350.
//
// Usage (one browser, polite delays; never bypasses a bot check: a blocked search is skipped):
//   node tools/fetch-shots.mjs mobile-backfill               top N shots for each m01-m30 search in mobile/INDEX.md
//   node tools/fetch-shots.mjs web    WANT "term a" "term b" -- "spare a" ...   new searches w(next)+
//   node tools/fetch-shots.mjs mobile WANT "term a" "term b" -- "spare a" ...   new searches m(next)+
// New searches that come up short (< N fresh 1800px shots) are dropped and the next spare is used.
// Resumable: a term already in the target INDEX.md is skipped. Internal reference only, never publish.
import { createRequire } from 'module';
import { readFileSync, writeFileSync, appendFileSync, existsSync, unlinkSync, mkdirSync } from 'fs';
import { execFileSync } from 'child_process';
// Playwright is resolved from PLAYWRIGHT_FROM (a package.json next to a node_modules with playwright) or the cwd.
const require = createRequire(process.env.PLAYWRIGHT_FROM || (process.cwd() + '/package.json'));
const { chromium } = require('playwright');
// The library root (holds web-shots/, mobile-shots/, mobile/). Set DRIBBBLE_LIB; never point it inside a public repo.
const root = (process.env.DRIBBBLE_LIB || decodeURIComponent(new URL('..', import.meta.url).pathname)).replace(/\/?$/, '/');
const N = Number(process.env.N ?? 5);
const W = 1800, H = 1350;
const sleep = ms => new Promise(r => setTimeout(r, ms));

const [mode, ...rest] = process.argv.slice(2);
if (!['mobile-backfill', 'web', 'mobile'].includes(mode)) { console.error('usage: fetch-shots.mjs mobile-backfill | web|mobile WANT terms... -- spares...'); process.exit(2); }
const kind = mode === 'web' ? 'web' : 'mobile';
const out = root + (kind === 'web' ? 'web-shots/' : 'mobile-shots/'); mkdirSync(out, { recursive: true });
const indexPath = out + 'INDEX.md';
const prefix = kind === 'web' ? 'w' : 'm';

const read = f => existsSync(f) ? readFileSync(f, 'utf8') : '';
const allIdx = read(root + 'web-shots/INDEX.md') + read(root + 'mobile-shots/INDEX.md');
const seen = new Set([...allIdx.matchAll(/https:\/\/dribbble\.com\/shots\/(\d+)/g)].map(m => m[1]));
const own = read(indexPath);
const doneTerms = new Set([...own.matchAll(/^\| `[wm]\d+-\d+-[^`]+` \| ([^|]+) \|/gm)].map(m => m[1].trim()));
const usedIds = [...own.matchAll(/^\| `([wm])(\d+)-\d+-/gm)].map(m => Number(m[2]));

let jobs, want = Infinity, strict;
if (mode === 'mobile-backfill') {
  jobs = [...read(root + 'mobile/INDEX.md').matchAll(/^\| (m\d+) \| ([^|]+) \|/gm)].map(m => ({ tag: m[1], q: m[2].trim() }));
  strict = false; // the m01-m30 ids are fixed, so a short search keeps what it found
} else {
  want = Number(rest[0]); const sep = rest.indexOf('--');
  const primary = rest.slice(1, sep < 0 ? undefined : sep), spares = sep < 0 ? [] : rest.slice(sep + 1);
  jobs = [...primary, ...spares].map(q => ({ q }));
  strict = true;
}
let nextId = Math.max(kind === 'web' ? 62 : 30, ...usedIds) + 1;
console.log(mode, 'existing shots', seen.size, 'next id', nextId);

const shotId = u => (u.match(/\/shots\/(\d+)/) || [])[1];
const dims = f => execFileSync('sips', ['-g', 'pixelWidth', '-g', 'pixelHeight', f]).toString().match(/\d+/g).slice(-2).map(Number);
const rows = [], skipped = [], tooSmall = new Set(); // tooSmall: shot ids already rejected on size this run
let saved = 0, filled = 0;

const b = await chromium.launch();
try {
  const p = await b.newPage({ viewport: { width: 1440, height: 1000 }, userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' });
  for (const job of jobs) {
    if (filled >= want) break;
    const q = job.q;
    if (doneTerms.has(q)) { console.log('already fetched', q); if (strict) filled++; continue; }
    const slug = q.replace(/\s+/g, '-');
    const url = `https://dribbble.com/search/${encodeURIComponent(slug)}`;
    try {
      const resp = await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 }); await p.waitForTimeout(4000);
      const title = await p.title();
      if (!resp || resp.status() >= 400 || /just a moment|attention required|captcha|verify you are human|access denied/i.test(title)) {
        skipped.push(`${q} (blocked: HTTP ${resp?.status()} "${title}")`); console.log('BLOCKED, skipping', q); await sleep(5000); continue;
      }
      for (let i = 0; i < 3; i++) { await p.mouse.wheel(0, 2500); await p.waitForTimeout(1500); }
      const shots = await p.evaluate(() => [...document.querySelectorAll('li.shot-thumbnail, li[id^="screenshot-"]')].filter(li =>
        !/boosted|promoted|sponsor|\bad\b/i.test(li.className) && !li.querySelector('[class*="boosted"], [class*="sponsor"], [data-ad]')).map(li => {
        const img = li.querySelector('.shot-thumbnail-base img, figure img, img[src*="/userupload/"]') || li.querySelector('img');
        return { href: li.querySelector('a[href*="/shots/"]')?.href, title: li.querySelector('.shot-title')?.textContent?.trim() || img?.alt || '',
          img: img?.getAttribute('src') || '', author: li.querySelector('.display-name')?.textContent?.trim() || '' };
      }).filter(s => s.href && s.img.includes('cdn.dribbble.com/userupload/')));
      const tag = job.tag || `${prefix}${String(nextId).padStart(2, '0')}`;
      const mine = [];
      for (const s of shots) {
        if (mine.length >= N) break;
        const sid = shotId(s.href);
        if (!sid || seen.has(sid) || tooSmall.has(sid)) continue;
        if (/\.(gif|mp4)$/i.test(s.img.split('?')[0])) continue; // animated files: sips keeps one frame only
        const base = s.img.split('?')[0];
        await sleep(400);
        const res = await fetch(`${base}?resize=${W}x${H}&vertical=center`, { headers: { 'user-agent': 'Mozilla/5.0' } });
        if (!res.ok) continue;
        const name = `${tag}-${String(mine.length + 1).padStart(2, '0')}-${slug}`;
        const tmp = out + name + '.src'; writeFileSync(tmp, Buffer.from(await res.arrayBuffer()));
        try { execFileSync('sips', ['-s', 'format', 'jpeg', '-s', 'formatOptions', '88', tmp, '--out', out + name + '.jpg'], { stdio: 'ignore' }); }
        catch { unlinkSync(tmp); continue; }
        unlinkSync(tmp);
        const [w, h] = dims(out + name + '.jpg');
        if (w !== W || h !== H) { unlinkSync(out + name + '.jpg'); tooSmall.add(sid); console.log('  skip', sid, `${w}x${h}`); continue; }
        mine.push({ sid, row: `| \`${name}.jpg\` | ${q} | [${s.title.replace(/[|[\]]/g, '/').replace(/\s+/g, ' ')}](${s.href.split('?')[0]}) | ${s.author.replace(/\|/g, '/')} |` });
        seen.add(sid);
      }
      if (strict && mine.length < N) { // not enough fresh full-res shots: drop this term, keep the id for the next one
        for (const m of mine) { const f = m.row.match(/`([^`]+)`/)[1]; if (existsSync(out + f)) unlinkSync(out + f); seen.delete(m.sid); }
        skipped.push(`${q} (only ${mine.length} new ${W}px shots)`); console.log('SHORT, skipping', q, mine.length); await sleep(3000); continue;
      }
      if (!mine.length) { skipped.push(`${q} (no new ${W}px shots)`); console.log('EMPTY', q); await sleep(3000); continue; }
      if (mine.length < N) skipped.push(`${tag} ${q} (kept ${mine.length} of ${N})`);
      rows.push({ tag, q, url, mine: mine.map(m => m.row) }); saved += mine.length; filled++;
      if (!job.tag) nextId++;
      console.log(tag, q, mine.length);
      await sleep(3000);
    } catch (e) { skipped.push(`${q} (error: ${e.message.slice(0, 80)})`); console.log(q, 'FAILED', e.message.slice(0, 100)); }
  }
} finally {
  await b.close();
  if (rows.length) {
    if (!existsSync(indexPath)) writeFileSync(indexPath, `# Mobile shots (individual, ${W}x${H})\n\nIndividual full-res mobile shots, ` +
      `fetched by \`tools/fetch-shots.mjs\`. Same format as [../web-shots/INDEX.md](../web-shots/INDEX.md). ` +
      `Other designers' work: internal reference only, never publish or ship.\n`);
    const span = `${rows[0].tag}-${rows[rows.length - 1].tag}`;
    const what = mode === 'mobile-backfill' ? `top shots of the [../mobile/INDEX.md](../mobile/INDEX.md) searches` : 'new searches';
    appendFileSync(indexPath, `\n## ${span} ${what}, fetched ${new Date().toISOString().slice(0, 10)} (tools/fetch-shots.mjs)\n\n` +
      `Top ${N} new shots per search (no ads), de-duplicated against every shot in web-shots/ and mobile-shots/; only exact ${W}x${H} images kept.\n\n` +
      `| # | Search | Source |\n|---|---|---|\n${rows.map(r => `| ${r.tag} | ${r.q} | [${r.url.replace('https://', '')}](${r.url}) |`).join('\n')}\n\n` +
      `| File | Search | Shot | Author |\n|---|---|---|---|\n${rows.flatMap(r => r.mine).join('\n')}\n`);
  }
  console.log('saved', saved, 'searches', rows.length); if (skipped.length) console.log('skipped:\n ' + skipped.join('\n '));
}
