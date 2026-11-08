// Run with mcp__claude-in-chrome__javascript_tool on the gemini.google.com tab after the Veo clip has rendered.
// Downloads the newest <video> to ~/Downloads/<NAME>.
const NAME = 'product-hero.mp4';
const vids = [...document.querySelectorAll('video')].filter(v => v.currentSrc || v.src || v.querySelector('source'));
if (!vids.length) throw new Error('No video on the page yet (Veo takes 1-3 minutes)');
const v = vids[vids.length - 1];
const src = v.currentSrc || v.src || v.querySelector('source').src;
const blob = await (await fetch(src, { credentials: 'include' })).blob();
const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: NAME });
document.body.appendChild(a); a.click(); a.remove();
`${NAME}: ${blob.type}, ${(blob.size / 1e6).toFixed(1)} MB, ${v.videoWidth}x${v.videoHeight}, ${v.duration.toFixed(1)} s`;
