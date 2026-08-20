# Little Desk - Sovereign Design Triage Node

A local, privacy-first email triage dashboard for interior architects. Uses local LLM (Ollama/Poolside) to extract change logs and draft replies, with a "Safe Loop" that requires PIN authorization and opens the native email client for manual sending.

## Features

- **IMAP Ingestion**: Automatically fetches emails from your "Design Revisions" folder
- **Local LLM Processing**: Extracts change logs and drafts replies using Poolside via Ollama
- **Field Journal Aesthetic**: Elegant, tactile UI with warm stone colors and serif typography
- **Safe Loop**: PIN-protected approval that opens native email client (never auto-sends)
- **Zero Telemetry**: All processing happens locally, no external API calls

## Quick Start

### Prerequisites

1. Python 3.11+
2. Ollama installed and running with Poolside model:
   ```bash
   ollama pull poolside
   ollama serve
   ```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your IMAP settings
```

### Configuration

Edit `.env`:

```env
# IMAP Settings
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=your@email.com
IMAP_PASSWORD=your-app-password
IMAP_FOLDER=Design Revisions

# Security (change on first use!)
DEFAULT_PIN=0000
```

### Running

```bash
# Start the server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Open in browser
open http://127.0.0.1:8000
```

## Project Structure

```
/workspace
├── app/
│   ├── __init__.py          # Package exports
│   ├── config.py            # Pydantic settings
│   ├── database.py          # SQLModel/SQLite setup
│   ├── models.py            # Database models
│   ├── main.py              # FastAPI app & routes
│   ├── llm.py               # Ollama client
│   ├── llm_worker.py        # Background LLM processing
│   ├── email_ingestion.py   # IMAP ingestion worker
│   ├── native_email.py      # OS-level email draft injection
│   └── security.py          # PIN hashing & verification
├── templates/
│   ├── dashboard.html       # Main split-screen layout
│   └── partials/
│       ├── _email_item.html # Email card component
│       ├── _pin_modal.html  # PIN entry modal
│       └── _settings_modal.html
├── docs/                    # Documentation suite
│   ├── Claude.md           # Master context & rules
│   ├── SPEC.md             # Technical architecture
│   ├── DESIGN.md           # UI/UX guidelines
│   ├── REVIEW.md           # Code review checklist
│   ├── SKILLS.md           # Agent capabilities
│   └── TASKS.md            # Implementation phases
├── static/                  # Static assets
├── requirements.txt
└── README.md
```

## The Safe Loop

**CRITICAL**: This system NEVER sends emails automatically.

1. User reviews AI-drafted reply in dashboard
2. User clicks "Authorize Execution"
3. User enters PIN (default: `0000`)
4. System opens native email client (Apple Mail / Outlook / etc.) with pre-filled draft
5. **User must manually click Send** in their email client

This ensures human oversight for all communications.

## Tech Stack

- **Backend**: FastAPI, Uvicorn, SQLModel, SQLite
- **Frontend**: Jinja2, HTMX, Tailwind CSS
- **AI**: Ollama/vLLM (local REST API)
- **Email**: `imaplib` for ingestion, OS subprocess for draft injection

## Security Checklist

See `docs/REVIEW.md` for the complete review checklist.

Key points:
- No external API calls (except local Ollama)
- PIN required for all approvals
- No SMTP library used
- Attachments confined to `~/Projects` directory

## License

MIT