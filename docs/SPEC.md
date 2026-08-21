## System Architecture
1. **Ingestion Worker**: Async background task running every 60s. Connects via IMAP, fetches unseen emails from "Design Revisions" folder. Downloads attachments to `~/Projects/[Client]/Revisions/[Date]`. Saves email metadata to SQLite.
2. **LLM Processor**: Reads email body from SQLite. Calls local Ollama API with a strict system prompt to extract: `Client Name`, `Project`, `Change Log (bullet points)`, `Drafted Reply`. Updates SQLite record.
3. **Dashboard (FastAPI + Jinja2)**: 
   - Serves the main split-screen layout.
   - Uses HTMX to poll/fetch pending items.
   - Left pane: Original email text + attachment thumbnails.
   - Right pane: AI Extracted Change Log + Drafted Reply.
4. **Safe Loop Execution**: 
   - User enters PIN in a modal.
   - FastAPI verifies PIN (hashed in SQLite).
   - FastAPI executes OS-level command to open native Mail client (e.g., AppleScript for Mac Mail, or `mailto:` fallback) with the drafted subject and body.
   - SQLite record marked as `status: approved`.

## Data Models (SQLite)
- `Email`: id, sender, subject, body, received_at, attachment_paths, status (pending, processing, ready, approved).
- `Draft`: id, email_id, change_log (JSON), drafted_reply, created_at.
- `AuditLog`: id, action, timestamp, ip_address (localhost).
