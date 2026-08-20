## Pre-Commit Review Checklist
Before marking any task as complete, verify the following:

### Security & Sovereignty (The Little Desk Constitution)
- [ ] **No External Leaks**: Are there any `requests.get/post` calls to external domains? (Must be 0, except local Ollama).
- [ ] **PIN Enforcement**: Does the `/api/approve` route explicitly check the PIN hash before executing the OS command?
- [ ] **No Auto-Send**: Is there any SMTP library (`smtplib`) imported or used? (Must be 0).
- [ ] **Local File Isolation**: Are downloaded attachments strictly confined to the configured `~/Projects` directory? (Check for path traversal vulnerabilities in the download logic).

### UX & Aesthetic
- [ ] **Field Journal Feel**: Are we using pure white (`bg-white`) anywhere? (Must be `bg-stone-50` or warmer).
- [ ] **HTMX Graceful Degradation**: If JS fails, does the page still render the initial state via Jinja2?
- [ ] **Split Screen**: Does the UI correctly handle long email bodies without breaking the layout? (Use `overflow-y-auto` with custom subtle scrollbars).
