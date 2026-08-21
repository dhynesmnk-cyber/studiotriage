import asyncio
import imaplib
import email
from email.header import decode_header
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
import json

from sqlmodel import Session, select

from .config import settings
from .models import Email as EmailModel
from .database import engine


def decode_mime_words(s: str) -> str:
    """Decode MIME encoded words in email headers."""
    decoded = []
    for part, encoding in decode_header(s):
        if isinstance(part, bytes):
            try:
                decoded.append(part.decode(encoding or 'utf-8'))
            except (UnicodeDecodeError, LookupError):
                decoded.append(part.decode('utf-8', errors='replace'))
        else:
            decoded.append(part)
    return ''.join(decoded)


def get_email_body(msg: email.message.Message) -> str:
    """Extract the body text from an email message."""
    body = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition") or "")
            
            # Skip attachments
            if "attachment" in content_disposition:
                continue
            
            if content_type == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                    break
                except Exception:
                    pass
            elif content_type == "text/html" and not body:
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                except Exception:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode('utf-8', errors='replace')
        except Exception:
            body = str(msg.get_payload())
    
    return body


def save_attachments(msg: email.message.Message, client_name: str = "Unknown", project_name: str = "Unknown") -> List[str]:
    """Save email attachments to local storage and return paths."""
    saved_paths = []
    base_dir = settings.PROJECTS_ROOT / client_name / project_name / "Revisions" / datetime.now().strftime("%Y-%m-%d")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition") or "")
        
        if "attachment" in content_disposition:
            filename = part.get_filename()
            if filename:
                filename = decode_mime_words(filename)
                # Sanitize filename
                filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
                
                filepath = base_dir / filename
                try:
                    data = part.get_payload(decode=True)
                    if data:
                        filepath.write_bytes(data)
                        saved_paths.append(str(filepath))
                except Exception as e:
                    print(f"Error saving attachment {filename}: {e}")
    
    return saved_paths


async def fetch_emails_async() -> List[Tuple[dict, List[str]]]:
    """
    Fetch unseen emails from IMAP server asynchronously.
    Returns list of tuples: (email_data_dict, attachment_paths)
    """
    if not settings.IMAP_SERVER:
        return []
    
    loop = asyncio.get_event_loop()
    
    def _fetch_imap() -> List[Tuple[dict, List[str]]]:
        results = []
        
        try:
            mail = imaplib.IMAP4_SSL(settings.IMAP_SERVER, settings.IMAP_PORT)
            mail.login(settings.IMAP_USERNAME, settings.IMAP_PASSWORD)
            mail.select(settings.IMAP_FOLDER)
            
            # Search for unseen emails
            status, messages = mail.search(None, "UNSEEN")
            
            if status != "OK":
                return []
            
            email_ids = messages[0].split()
            
            for email_id in email_ids[-10:]:  # Limit to last 10 emails
                try:
                    status, msg_data = mail.fetch(email_id, "(RFC822)")
                    if status != "OK":
                        continue
                    
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    sender = decode_mime_words(msg.get("From", ""))
                    subject = decode_mime_words(msg.get("Subject", ""))
                    body = get_email_body(msg)
                    
                    # Try to extract client/project from subject
                    client_project = "Unknown/Unknown"
                    if ":" in subject:
                        client_project = subject.split(":")[0].strip()
                    
                    client_name, project_name = client_project.split("/") if "/" in client_project else (client_project, "General")
                    
                    attachments = save_attachments(msg, client_name, project_name)
                    
                    email_data = {
                        "sender": sender,
                        "subject": subject,
                        "body": body,
                        "received_at": datetime.utcnow(),
                        "attachment_paths": json.dumps(attachments),
                        "status": "pending"
                    }
                    
                    results.append((email_data, attachments))
                    
                except Exception as e:
                    print(f"Error processing email {email_id}: {e}")
                    continue
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            print(f"IMAP connection error: {e}")
        
        return results
    
    return await loop.run_in_executor(None, _fetch_imap)


async def ingest_emails_worker():
    """Background worker that periodically fetches emails and saves to database."""
    while True:
        try:
            fetched = await fetch_emails_async()
            
            with Session(engine) as session:
                for email_data, attachments in fetched:
                    email_model = EmailModel(**email_data)
                    session.add(email_model)
                
                session.commit()
                
                if fetched:
                    print(f"Ingested {len(fetched)} new emails")
        
        except Exception as e:
            print(f"Email ingestion error: {e}")
        
        await asyncio.sleep(settings.IMAP_POLL_INTERVAL)
