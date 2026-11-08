# Putting a long prompt into grok.com

Grok's composer is a contenteditable `div`. Typing a long prompt key by key is slow, and newlines send it early.
Insert the text in one call instead.

1. JSON-encode the prompt file so the quotes and newlines survive:

   ```bash
   python3 -c "import json;print(json.dumps(open('brief-lens3.md').read()))"
   ```

2. Paste the output in place of `PROMPT_JSON` below and run it with `javascript_tool` in the Grok tab:

   ```js
   const txt = PROMPT_JSON;
   const el = document.querySelector('textarea, [contenteditable="true"]');
   el.focus();
   if (el.tagName === 'TEXTAREA') {
     Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set.call(el, txt);
     el.dispatchEvent(new Event('input', { bubbles: true }));
   } else {
     document.execCommand('insertText', false, txt);
   }
   el.tagName + ' ' + (el.value || el.innerText).length
   ```

3. Check that the returned length roughly matches the file's length. Then press Return with `computer`
   (`key: "Return"`).

4. To read the answer, use `get_page_text`, or this to get only the text after your prompt:

   ```js
   const t = document.body.innerText;
   t.slice(t.indexOf('LAST LINE OF YOUR PROMPT') + 40)
   ```

   An answer still streaming shows "Working for Ns" or "Thinking". Wait and read again.
