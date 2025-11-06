"""
Authentication service for JWT tokens, password hashing, and token management
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import secrets
import hashlib
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.user import User, UserRole
from app.models.auth import VerificationToken, RefreshToken, LoginAttempt

logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        logger.debug("Hashing password")
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches
        """
        result = pwd_context.verify(plain_password, hashed_password)
        logger.debug(f"Password verification result: {result}")
        return result
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token
        
        Args:
            data: Data to encode in token
            expires_delta: Token expiration time
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        # Convert sub to string if it's an int (JWT spec requires string)
        if "sub" in to_encode and isinstance(to_encode["sub"], int):
            to_encode["sub"] = str(to_encode["sub"])
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        logger.info(f"Created access token for user_id={data.get('sub')}, expires_at={expire.isoformat()}")
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(
        user_id: int,
        db: Session,
        device_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        remember_me: bool = False
    ) -> str:
        """
        Create and store refresh token
        
        Args:
            user_id: User ID
            db: Database session
            device_id: Device identifier
            user_agent: User agent string
            ip_address: IP address
            remember_me: Extended expiration if True
            
        Returns:
            Refresh token string
        """
        logger.info(f"Creating refresh token for user_id={user_id}, remember_me={remember_me}, ip={ip_address}")
        
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        
        # Set expiration
        if remember_me:
            expires_delta = timedelta(days=30)  # 30 days for "remember me"
        else:
            expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        expires_at = datetime.now(timezone.utc) + expires_delta
        
        # Store refresh token
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            device_id=device_id,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        db.add(refresh_token)
        db.commit()
        
        logger.debug(f"Refresh token created, expires_at={expires_at.isoformat()}")
        return token
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token data or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            return None
    
    @staticmethod
    def generate_verification_token(
        user_id: int,
        token_type: str,
        db: Session,
        expires_in_hours: int = 24
    ) -> str:
        """
        Generate email verification or password reset token
        
        Args:
            user_id: User ID
            token_type: Type of token ('email_verification' or 'password_reset')
            db: Database session
            expires_in_hours: Token expiration in hours
            
        Returns:
            Verification token string
        """
        logger.info(f"Generating {token_type} token for user_id={user_id}, expires_in={expires_in_hours}h")
        
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        
        # Set expiration
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
        
        # Store token
        verification_token = VerificationToken(
            user_id=user_id,
            token=token,
            token_type=token_type,
            expires_at=expires_at
        )
        
        db.add(verification_token)
        db.commit()
        
        logger.debug(f"Verification token created: type={token_type}, expires_at={expires_at.isoformat()}")
        return token
    
    @staticmethod
    def verify_verification_token(
        token: str,
        token_type: str,
        db: Session
    ) -> Optional[VerificationToken]:
        """
        Verify a verification/reset token
        
        Args:
            token: Token string
            token_type: Expected token type
            db: Database session
            
        Returns:
            VerificationToken object if valid, None otherwise
        """
        logger.info(f"Verifying {token_type} token")
        
        verification_token = db.query(VerificationToken).filter(
            VerificationToken.token == token,
            VerificationToken.token_type == token_type
        ).first()
        
        if not verification_token:
            logger.warning(f"Token not found: type={token_type}")
            return None
        
        if not verification_token.is_valid:
            logger.warning(f"Token invalid or expired: type={token_type}, user_id={verification_token.user_id}")
            return None
        
        logger.info(f"Token verified successfully: type={token_type}, user_id={verification_token.user_id}")
        return verification_token
    
    @staticmethod
    def mark_token_as_used(token: VerificationToken, db: Session):
        """Mark a verification token as used"""
        token.used = True
        token.used_at = datetime.now(timezone.utc)
        db.commit()
    
    @staticmethod
    def revoke_refresh_token(token: str, db: Session) -> bool:
        """
        Revoke a refresh token
        
        Args:
            token: Refresh token string
            db: Database session
            
        Returns:
            True if token was revoked, False if not found
        """
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token == token
        ).first()
        
        if not refresh_token:
            return False
        
        refresh_token.revoked = True
        refresh_token.revoked_at = datetime.now(timezone.utc)
        db.commit()
        
        return True
    
    @staticmethod
    def revoke_all_user_tokens(user_id: int, db: Session):
        """Revoke all refresh tokens for a user"""
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False
        ).update({
            "revoked": True,
            "revoked_at": datetime.now(timezone.utc)
        })
        db.commit()
    
    @staticmethod
    def log_login_attempt(
        email: str,
        success: bool,
        db: Session,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None
    ):
        """
        Log a login attempt
        
        Args:
            email: User email
            success: Whether login was successful
            db: Database session
            ip_address: IP address
            user_agent: User agent string
            failure_reason: Reason for failure if applicable
        """
        login_attempt = LoginAttempt(
            email=email,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason=failure_reason
        )
        
        db.add(login_attempt)
        db.commit()
    
    @staticmethod
    def check_login_attempts(email: str, db: Session, window_minutes: int = 15, max_attempts: int = 5) -> bool:
        """
        Check if user has exceeded login attempts
        
        Args:
            email: User email
            db: Database session
            window_minutes: Time window to check
            max_attempts: Maximum allowed attempts
            
        Returns:
            True if too many attempts, False otherwise
        """
        since = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
        
        attempts = db.query(LoginAttempt).filter(
            LoginAttempt.email == email,
            LoginAttempt.success == False,
            LoginAttempt.attempted_at >= since
        ).count()
        
        return attempts >= max_attempts
    
    @staticmethod
    def authenticate_user(email: str, password: str, db: Session) -> Optional[User]:
        """
        Authenticate a user
        
        Args:
            email: User email
            password: Plain text password
            db: Database session
            
        Returns:
            User object if authenticated, None otherwise
        """
        logger.info(f"Authenticating user: email={email}")
        
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            logger.warning(f"Authentication failed: User not found - email={email}")
            return None
        
        if not AuthService.verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: Invalid password - email={email}, user_id={user.id}")
            return None
        
        if not user.is_active:
            logger.warning(f"Authentication failed: User inactive - email={email}, user_id={user.id}")
            return None
        
        # Check admin approval for doctors
        if user.role == UserRole.DOCTOR and not user.admin_approved:
            logger.warning(f"Authentication failed: Doctor not approved by admin - email={email}, user_id={user.id}")
            return None
        
        logger.info(f"Authentication successful: email={email}, user_id={user.id}, role={user.role}")
        return user
    
    @staticmethod
    def get_user_from_token(token: str, db: Session) -> Optional[User]:
        """
        Get user from JWT token
        
        Args:
            token: JWT token string
            db: Database session
            
        Returns:
            User object if token is valid, None otherwise
        """
        payload = AuthService.verify_token(token)
        
        if not payload:
            return None
        
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
        
        # Convert sub back to int
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        return user


# Singleton instance
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Get singleton auth service instance"""
    global _auth_service
    
    if _auth_service is None:
        _auth_service = AuthService()
    
    return _auth_service
