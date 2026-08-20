import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import Annotated
from datetime import datetime
import json

from .database import get_session, create_db_and_tables, SessionLocal
from .models import Email, Draft, AuditLog, PINConfig
from .security import verify_pin, initialize_default_pin, set_pin, get_pin_config
from .native_email import create_draft_from_email
from .config import settings
from .email_ingestion import ingest_emails_worker
from .llm_worker import process_pending_emails


# Background task managers
ingest_task = None
llm_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events."""
    # Startup
    create_db_and_tables()
    
    db = SessionLocal()
    try:
        initialize_default_pin(db, settings.DEFAULT_PIN)
    finally:
        db.close()
    
    # Start background workers
    global ingest_task, llm_task
    ingest_task = asyncio.create_task(ingest_emails_worker())
    llm_task = asyncio.create_task(process_pending_emails())
    
    yield
    
    # Shutdown
    if ingest_task:
        ingest_task.cancel()
        try:
            await ingest_task
        except asyncio.CancelledError:
            pass
    
    if llm_task:
        llm_task.cancel()
        try:
            await llm_task
        except asyncio.CancelledError:
            pass


# Initialize FastAPI app with lifespan
app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# Setup templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Annotated[Session, Depends(get_session)]):
    """Main dashboard view - split screen layout."""
    
    # Get all ready emails with drafts
    statement = (
        select(Email)
        .where(Email.status == "ready")
        .order_by(Email.received_at.desc())
    )
    emails = db.exec(statement).all()
    
    email_data = []
    for email in emails:
        draft_statement = select(Draft).where(Draft.email_id == email.id)
        draft = db.exec(draft_statement).first()
        
        if draft:
            change_log = json.loads(draft.change_log)
            attachment_paths = json.loads(email.attachment_paths)
            
            email_data.append({
                "id": email.id,
                "sender": email.sender,
                "subject": email.subject,
                "body": email.body,
                "received_at": email.received_at,
                "attachments": attachment_paths,
                "change_log": change_log.get("changes", []),
                "client_name": change_log.get("client_name"),
                "project": change_log.get("project"),
                "drafted_reply": draft.drafted_reply
            })
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "emails": email_data,
            "app_name": settings.APP_NAME
        }
    )


@app.get("/emails/{email_id}/partial", response_class=HTMLResponse)
async def email_partial(
    email_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_session)]
):
    """HTMX partial: render a single email item for the list."""
    
    email = db.get(Email, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    draft_statement = select(Draft).where(Draft.email_id == email_id)
    draft = db.exec(draft_statement).first()
    
    if not draft:
        return HTMLResponse(content="", status_code=404)
    
    change_log = json.loads(draft.change_log)
    attachment_paths = json.loads(email.attachment_paths)
    
    return templates.TemplateResponse(
        "partials/_email_item.html",
        {
            "request": request,
            "email": {
                "id": email.id,
                "sender": email.sender,
                "subject": email.subject,
                "body": email.body,
                "received_at": email.received_at,
                "attachments": attachment_paths,
                "change_log": change_log.get("changes", []),
                "client_name": change_log.get("client_name"),
                "project": change_log.get("project"),
                "drafted_reply": draft.drafted_reply
            }
        }
    )


@app.post("/api/approve/{email_id}")
async def approve_email(
    email_id: int,
    request: Request,
    pin: Annotated[str, Form()],
    db: Annotated[Session, Depends(get_session)]
):
    """
    Safe Loop: Approve an email draft.
    CRITICAL: This opens the native email client with a draft. It does NOT send automatically.
    """
    
    # Verify PIN
    pin_config = get_pin_config(db)
    if not pin_config or not verify_pin(pin, pin_config.pin_hash):
        raise HTTPException(status_code=401, detail="Invalid PIN")
    
    # Get email and draft
    email = db.get(Email, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    draft_statement = select(Draft).where(Draft.email_id == email_id)
    draft = db.exec(draft_statement).first()
    
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    # Open native email client with draft (DOES NOT SEND)
    success = create_draft_from_email(email, draft)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to open email client")
    
    # Update status to approved
    email.status = "approved"
    db.add(email)
    
    # Log the action
    audit_log = AuditLog(
        action="approve_email",
        ip_address="127.0.0.1",
        details=f"Approved email {email_id} from {email.sender}"
    )
    db.add(audit_log)
    
    db.commit()
    
    return {"success": True, "message": "Draft opened in native email client"}


@app.get("/api/emails/count")
async def get_ready_count(db: Annotated[Session, Depends(get_session)]):
    """HTMX polling endpoint: return count of ready emails."""
    statement = select(Email).where(Email.status == "ready")
    emails = db.exec(statement).all()
    return {"count": len(emails)}


@app.get("/approve/modal/{email_id}", response_class=HTMLResponse)
async def approve_modal(email_id: int, request: Request):
    """Render PIN entry modal for approving an email."""
    return templates.TemplateResponse(
        "partials/_pin_modal.html",
        {"request": request, "email_id": email_id}
    )


@app.get("/settings/pin-modal", response_class=HTMLResponse)
async def settings_pin_modal(request: Request):
    """Render settings modal for changing PIN."""
    return templates.TemplateResponse(
        "partials/_settings_modal.html",
        {"request": request}
    )


@app.post("/api/pin/change")
async def change_pin(
    request: Request,
    current_pin: Annotated[str, Form()],
    new_pin: Annotated[str, Form()],
    db: Annotated[Session, Depends(get_session)]
):
    """Change the PIN for the Safe Loop."""
    
    pin_config = get_pin_config(db)
    if not pin_config or not verify_pin(current_pin, pin_config.pin_hash):
        raise HTTPException(status_code=401, detail="Current PIN is invalid")
    
    set_pin(db, new_pin)
    
    # Log the action
    audit_log = AuditLog(
        action="change_pin",
        ip_address="127.0.0.1",
        details="PIN changed successfully"
    )
    db.add(audit_log)
    db.commit()
    
    return {"success": True, "message": "PIN updated"}
