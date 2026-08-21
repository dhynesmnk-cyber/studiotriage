from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import json


class Email(SQLModel, table=True):
    __tablename__ = "emails"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    sender: str
    subject: str
    body: str
    received_at: datetime = Field(default_factory=datetime.utcnow)
    attachment_paths: str = Field(default="[]")  # JSON encoded list
    status: str = Field(default="pending")  # pending, processing, ready, approved
    
    draft: Optional["Draft"] = Relationship(back_populates="email")


class Draft(SQLModel, table=True):
    __tablename__ = "drafts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email_id: int = Field(foreign_key="emails.id")
    change_log: str = Field(default="{}")  # JSON encoded dict
    drafted_reply: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    email: Optional[Email] = Relationship(back_populates="draft")


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    action: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: str = Field(default="127.0.0.1")
    details: str = Field(default="")


class PINConfig(SQLModel, table=True):
    __tablename__ = "pin_config"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    pin_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
