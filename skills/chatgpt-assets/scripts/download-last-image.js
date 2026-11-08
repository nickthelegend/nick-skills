// Run with mcp__claude-in-chrome__javascript_tool on the chatgpt.com tab once the image has rendered.
// Downloads the newest generated image to ~/Downloads/<NAME>.
const NAME = 'product-hero.png';
const imgs = [...document.querySelectorAll('img')].filter(i =>
  /generated image/i.test(i.alt || '') || /oaiusercontent|estuary|files\.oaiusercontent/.test(i.src));
if (!imgs.length) throw new Error('No generated image on the page yet');
const img = imgs[imgs.length - 1];
const blob = await (await fetch(img.src, { credentials: 'include' })).blob();
const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: NAME });
document.body.appendChild(a); a.click(); a.remove();
`${NAME}: ${blob.type}, ${Math.round(blob.size / 1024)} KB, ${img.naturalWidth}x${img.naturalHeight}`;
