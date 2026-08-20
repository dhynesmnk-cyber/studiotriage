## Implementation Phases

### Phase 1: Foundation & Database
- [ ] Initialize FastAPI project with Uvicorn.
- [ ] Setup SQLModel/SQLAlchemy with SQLite. Define `Email`, `Draft`, and `AuditLog` tables.
- [ ] Create basic Jinja2 base template with Tailwind CSS configured for the "Field Journal" aesthetic.

### Phase 2: IMAP Ingestion Engine
- [ ] Write async IMAP connection logic.
- [ ] Implement attachment downloading to local structured directories (`~/Projects/...`).
- [ ] Create background task to poll IMAP and insert new emails into SQLite with `status: pending`.

### Phase 3: Local LLM Integration (The Engine)
- [ ] Write Ollama/vLLM client wrapper.
- [ ] Create prompt template for extracting changes and drafting replies.
- [ ] Build background worker that picks up `pending` emails, calls local LLM, saves `Draft`, and updates status to `ready`.

### Phase 4: The Dashboard (Frontend)
- [ ] Build the split-screen Jinja2 layout.
- [ ] Implement HTMX endpoints to fetch and render the list of `ready` emails.
- [ ] Build the Left Pane (Original email + attachment links).
- [ ] Build the Right Pane (Rendered Markdown change log + drafted reply).

### Phase 5: The Safe Loop (Auth & Execution)
- [ ] Implement PIN generation, hashing (bcrypt), and storage.
- [ ] Build the PIN entry modal (HTMX/Tailwind).
- [ ] Write the OS-level execution logic to open the native email client with the pre-filled draft.
- [ ] Wire up the `/api/approve` endpoint: Verify PIN -> Execute OS command -> Update DB to `approved` -> Log to Audit table.
