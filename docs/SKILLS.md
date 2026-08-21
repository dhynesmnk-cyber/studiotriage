## Agent Skills for this Codebase
When working on this project, utilize the following specific patterns:

1. **IMAP Async Parsing**: Use `aioimaplib` or run standard `imaplib` in a `run_in_executor` to prevent blocking the FastAPI event loop.
2. **HTMX Partial Rendering**: Never return full HTML for dynamic updates. Always return Jinja2 partials (e.g., `_email_row.html`) and use `hx-swap="outerHTML"`.
3. **OS-Level Draft Injection**: 
   - For macOS: Use `subprocess.run(['osascript', '-e', 'tell application "Mail"...'])` to create the draft.
   - Fallback: Use `webbrowser.open(f"mailto:{to}?subject={subj}&body={body}")` (Note: URL encode the body, keep it under 2000 chars for fallback).
4. **Local LLM Prompting**: When calling Ollama, use strict JSON mode or structured output parsing to ensure the `change_log` and `drafted_reply` are cleanly separated.
