// Run with mcp__claude-in-chrome__javascript_tool on a grok.com tab.
// Replace __PROMPT__ with a JSON string literal of the brief (python3 -c "import json;print(json.dumps(open('brief.md').read()))").
// Then press Return with a computer `key` action.
const txt = __PROMPT__;
const el = document.querySelector('textarea, [contenteditable="true"]');
if (!el) throw new Error('Grok composer not found: is the user signed in and on grok.com?');
el.focus();
if (el.tagName === 'TEXTAREA') {
  const set = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
  set.call(el, txt);
  el.dispatchEvent(new Event('input', { bubbles: true }));
} else {
  document.execCommand('insertText', false, txt);
}
`${el.tagName} holds ${(el.value || el.innerText).length} chars (prompt was ${txt.length})`;
