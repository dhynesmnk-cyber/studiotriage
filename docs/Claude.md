# Project: Little Desk - Sovereign Design Triage Node
## Context
We are building a local, privacy-first email triage dashboard for a solo interior architect. 
The system ingests high-end restaurant design backgrounds via IMAP, uses a local LLM (Poolside via Ollama) to extract change logs and draft replies, and presents them in a split-screen "Safe Loop" dashboard. 
CRITICAL: The AI NEVER sends emails directly. It opens the native OS email client with a pre-filled draft. The user must manually click send.

## Tech Stack
- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **Frontend**: Jinja2 templates, HTMX (for reactive partials without JS bloat), Tailwind CSS
- **Database**: SQLite (via SQLModel or SQLAlchemy) for audit logs and state
- **AI Engine**: Ollama/vLLM local REST API (OpenAI-compatible endpoint)
- **Email**: `imaplib` (async) for ingestion, OS-level subprocess (AppleScript/CLI) for native draft injection.

## Core Directives for the Coding Agent
1. **Zero Telemetry**: No external API calls for data processing. All LLM calls go to `localhost:11434` (or configured local port).
2. **The Safe Loop**: The `/approve` endpoint MUST require a PIN. It MUST NOT use SMTP to send. It MUST trigger a native OS draft.
3. **Aesthetic**: Strictly adhere to the "Field Journal" design system (see `DESIGN.md`). No generic SaaS UI.
4. **File Structure**: Keep backend logic in `/app`, templates in `/templates`, static assets in `/static`.
