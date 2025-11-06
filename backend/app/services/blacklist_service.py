"""
Email blacklist service for managing blocked emails
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.models.blacklist import EmailBlacklist, BlacklistReason
from app.core.logging import get_logger

logger = get_logger(__name__)


class BlacklistService:
    """Service for managing email blacklist"""
    
    @staticmethod
    def add_to_blacklist(
        email: str,
        reason: BlacklistReason,
        db: Session,
        details: Optional[str] = None,
        original_user_id: Optional[int] = None,
        original_user_name: Optional[str] = None,
        original_user_role: Optional[str] = None,
        admin_id: Optional[int] = None,
        admin_email: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> EmailBlacklist:
        """
        Add an email to the blacklist
        
        Args:
            email: Email address to blacklist
            reason: Reason for blacklisting
            db: Database session
            details: Additional details about the blacklisting
            original_user_id: ID of the original user (if applicable)
            original_user_name: Name of the original user
            original_user_role: Role of the original user
            admin_id: ID of the admin who blacklisted
            admin_email: Email of the admin who blacklisted
            expires_at: Optional expiration date
            
        Returns:
            EmailBlacklist object
        """
        logger.info(
            f"[BLACKLIST] Adding email to blacklist | "
            f"email={email} | reason={reason.value} | "
            f"admin={admin_email} | user_id={original_user_id}"
        )
        
        # Check if already blacklisted
        existing = db.query(EmailBlacklist).filter(
            EmailBlacklist.email == email.lower()
        ).first()
        
        if existing:
            logger.warning(
                f"[BLACKLIST] Email already blacklisted | "
                f"email={email} | existing_reason={existing.reason.value}"
            )
            # Update existing entry
            existing.reason = reason
            existing.details = details
            existing.blacklisted_by_admin_id = admin_id
            existing.blacklisted_by_admin_email = admin_email
            existing.expires_at = expires_at
            db.commit()
            db.refresh(existing)
            return existing
        
        # Create new blacklist entry
        blacklist_entry = EmailBlacklist(
            email=email.lower(),
            reason=reason,
            details=details,
            original_user_id=original_user_id,
            original_user_name=original_user_name,
            original_user_role=original_user_role,
            blacklisted_by_admin_id=admin_id,
            blacklisted_by_admin_email=admin_email,
            expires_at=expires_at
        )
        
        db.add(blacklist_entry)
        db.commit()
        db.refresh(blacklist_entry)
        
        logger.info(
            f"[BLACKLIST] Email successfully blacklisted | "
            f"blacklist_id={blacklist_entry.id} | email={email}"
        )
        
        return blacklist_entry
    
    @staticmethod
    def is_blacklisted(email: str, db: Session) -> tuple[bool, Optional[EmailBlacklist]]:
        """
        Check if an email is blacklisted
        
        Args:
            email: Email address to check
            db: Database session
            
        Returns:
            Tuple of (is_blacklisted, blacklist_entry)
        """
        blacklist_entry = db.query(EmailBlacklist).filter(
            EmailBlacklist.email == email.lower()
        ).first()
        
        if not blacklist_entry:
            return False, None
        
        # Check if expired
        if blacklist_entry.is_expired:
            logger.info(
                f"[BLACKLIST] Blacklist entry expired | "
                f"email={email} | expired_at={blacklist_entry.expires_at}"
            )
            return False, None
        
        logger.warning(
            f"[BLACKLIST] Email is blacklisted | "
            f"email={email} | reason={blacklist_entry.reason.value} | "
            f"blacklist_id={blacklist_entry.id}"
        )
        
        return True, blacklist_entry
    
    @staticmethod
    def remove_from_blacklist(email: str, db: Session, admin_email: Optional[str] = None) -> bool:
        """
        Remove an email from the blacklist
        
        Args:
            email: Email address to remove
            db: Database session
            admin_email: Email of the admin performing the action
            
        Returns:
            True if removed, False if not found
        """
        blacklist_entry = db.query(EmailBlacklist).filter(
            EmailBlacklist.email == email.lower()
        ).first()
        
        if not blacklist_entry:
            logger.warning(
                f"[BLACKLIST] Attempted to remove non-blacklisted email | "
                f"email={email} | admin={admin_email}"
            )
            return False
        
        logger.info(
            f"[BLACKLIST] Removing email from blacklist | "
            f"email={email} | reason={blacklist_entry.reason.value} | "
            f"admin={admin_email} | blacklist_id={blacklist_entry.id}"
        )
        
        db.delete(blacklist_entry)
        db.commit()
        
        logger.info(f"[BLACKLIST] Email removed from blacklist | email={email}")
        
        return True
    
    @staticmethod
    def get_blacklist_message(blacklist_entry: EmailBlacklist) -> str:
        """
        Get user-friendly message for blacklisted email
        
        Args:
            blacklist_entry: Blacklist entry
            
        Returns:
            User-friendly error message
        """
        messages = {
            BlacklistReason.DELETED: (
                "Ce compte a été définitivement supprimé. "
                "Vous ne pouvez plus utiliser cette adresse email pour vous inscrire. "
                "Si vous pensez qu'il s'agit d'une erreur, contactez le support."
            ),
            BlacklistReason.SUSPENDED: (
                "Ce compte est actuellement suspendu. "
                "Vous ne pouvez pas créer de nouveau compte ou vous connecter avec cette adresse email. "
                "Pour plus d'informations, contactez le support."
            ),
            BlacklistReason.BANNED: (
                "Cette adresse email a été bannie de notre plateforme. "
                "Pour plus d'informations, contactez le support."
            ),
            BlacklistReason.FRAUD: (
                "Cette adresse email a été signalée pour activité frauduleuse. "
                "Vous ne pouvez pas utiliser cette adresse email. "
                "Pour toute contestation, contactez le support."
            )
        }
        
        return messages.get(blacklist_entry.reason, "Cette adresse email ne peut pas être utilisée.")


# Singleton instance
_blacklist_service: Optional[BlacklistService] = None


def get_blacklist_service() -> BlacklistService:
    """Get singleton blacklist service instance"""
    global _blacklist_service
    
    if _blacklist_service is None:
        _blacklist_service = BlacklistService()
    
    return _blacklist_service
