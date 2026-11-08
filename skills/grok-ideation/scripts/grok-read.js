// Run with javascript_tool after Grok has finished (the stop button is gone).
// Returns everything after the end of your prompt; pass a distinctive last line of your prompt as MARKER.
const MARKER = 'Output Markdown only. No preamble.';
const t = document.body.innerText;
const i = t.lastIndexOf(MARKER);
(i < 0 ? t : t.slice(i + MARKER.length)).trim();
