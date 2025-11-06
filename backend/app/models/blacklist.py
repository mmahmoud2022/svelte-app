"""
Email blacklist model for deleted and suspended accounts
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class BlacklistReason(str, enum.Enum):
    """Reason for email blacklisting"""
    DELETED = "deleted"
    SUSPENDED = "suspended"
    BANNED = "banned"
    FRAUD = "fraud"


class EmailBlacklist(Base):
    """Email blacklist model"""
    __tablename__ = "email_blacklist"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Email address
    email = Column(String(255), unique=True, index=True, nullable=False)
    
    # Blacklist reason
    reason = Column(SQLEnum(BlacklistReason, values_callable=lambda x: [e.value for e in x]), nullable=False)
    
    # Additional details
    details = Column(Text, nullable=True)
    
    # Original user info (for reference)
    original_user_id = Column(Integer, nullable=True)
    original_user_name = Column(String(200), nullable=True)
    original_user_role = Column(String(50), nullable=True)
    
    # Admin who added to blacklist
    blacklisted_by_admin_id = Column(Integer, nullable=True)
    blacklisted_by_admin_email = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Optional expiration
    
    def __repr__(self):
        return f"<EmailBlacklist {self.email} ({self.reason})>"
    
    @property
    def is_expired(self):
        """Check if blacklist entry is expired"""
        if not self.expires_at:
            return False
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expires_at
