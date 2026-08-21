import bcrypt
from sqlmodel import Session, select

from .database import engine
from .models import PINConfig


def hash_pin(pin: str) -> str:
    """Hash a PIN using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pin.encode('utf-8'), salt).decode('utf-8')


def verify_pin(pin: str, pin_hash: str) -> bool:
    """Verify a PIN against its hash."""
    return bcrypt.checkpw(pin.encode('utf-8'), pin_hash.encode('utf-8'))


def get_pin_config(db: Session) -> PINConfig | None:
    """Get the current PIN configuration from the database."""
    statement = select(PINConfig).order_by(PINConfig.created_at.desc()).limit(1)
    return db.exec(statement).first()


def set_pin(db: Session, pin: str) -> PINConfig:
    """Set or update the PIN."""
    existing = get_pin_config(db)
    pin_hash = hash_pin(pin)
    
    if existing:
        existing.pin_hash = pin_hash
        db.add(existing)
    else:
        new_pin = PINConfig(pin_hash=pin_hash)
        db.add(new_pin)
    
    db.commit()
    db.refresh(existing or new_pin)
    return existing or new_pin


def initialize_default_pin(db: Session, default_pin: str) -> None:
    """Initialize the PIN with a default value if none exists."""
    if get_pin_config(db) is None:
        set_pin(db, default_pin)
