import asyncio
import json
from sqlmodel import Session, select

from .database import engine
from .models import Email as EmailModel, Draft as DraftModel
from .llm import ollama_client


async def process_pending_emails():
    """Background worker that processes pending emails with the local LLM."""
    while True:
        try:
            with Session(engine) as session:
                # Find all pending emails
                statement = select(EmailModel).where(EmailModel.status == "pending")
                pending_emails = session.exec(statement).all()
                
                for email_model in pending_emails:
                    # Update status to processing
                    email_model.status = "processing"
                    session.add(email_model)
                    session.commit()
                    
                    try:
                        # Call LLM to extract data and draft reply
                        extracted_data = await ollama_client.extract_email_data(email_model.body)
                        
                        # Create draft record
                        draft = DraftModel(
                            email_id=email_model.id,
                            change_log=json.dumps({
                                "client_name": extracted_data.get("client_name"),
                                "project": extracted_data.get("project"),
                                "changes": extracted_data.get("change_log", [])
                            }),
                            drafted_reply=extracted_data.get("drafted_reply", "")
                        )
                        session.add(draft)
                        
                        # Update email status to ready
                        email_model.status = "ready"
                        session.add(email_model)
                        session.commit()
                        
                        print(f"Processed email {email_model.id}")
                        
                    except Exception as e:
                        print(f"Error processing email {email_model.id}: {e}")
                        email_model.status = "pending"  # Revert to pending for retry
                        session.add(email_model)
                        session.commit()
        
        except Exception as e:
            print(f"LLM processing error: {e}")
        
        await asyncio.sleep(30)  # Check every 30 seconds
