"""
Authentication schemas for registration, login, password reset, and verification
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


# Base schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    gender: Optional[str] = Field(None, max_length=20)


# Registration schemas
class PatientRegister(UserBase):
    """Patient registration schema"""
    password: str = Field(..., min_length=8, max_length=100)
    date_of_birth: Optional[datetime] = None
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=100)
    marketing_consent: bool = False
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class PractitionerRegister(UserBase):
    """Practitioner/Doctor registration schema"""
    password: str = Field(..., min_length=8, max_length=100)
    specialization: str = Field(..., min_length=2, max_length=100)
    #license_number: str = Field(..., min_length=5, max_length=50)
    bio: Optional[str] = Field(None, max_length=2000)
    consultation_fee: Optional[int] = Field(None, ge=0)  # in cents
    languages_spoken: Optional[str] = None
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class AdminRegister(UserBase):
    """Admin registration schema (requires admin secret)"""
    password: str = Field(..., min_length=8, max_length=100)
    admin_secret: str = Field(..., description="Admin registration secret")
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


# Login schemas
class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str
    remember_me: bool = False
    device_id: Optional[str] = None


class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


# Token schemas
class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# Password reset schemas
class PasswordResetRequest(BaseModel):
    """Request password reset"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Confirm password reset with token"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class PasswordChange(BaseModel):
    """Change password (when logged in)"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


# Email verification schemas
class EmailVerificationRequest(BaseModel):
    """Request email verification"""
    email: EmailStr


class EmailVerificationConfirm(BaseModel):
    """Confirm email verification with token"""
    token: str


# User response schemas
class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole
    is_active: bool
    is_verified: bool
    admin_approved: bool = False
    profile_image: Optional[str] = None
    created_at: datetime
    
    # Role-specific fields
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    consultation_fee: Optional[int] = None
    rating_average: Optional[float] = None
    rating_count: Optional[int] = None
    accepting_new_patients: Optional[bool] = None
    
    model_config = {"from_attributes": True}


class UserDetailResponse(UserResponse):
    """Detailed user response with more fields"""
    date_of_birth: Optional[datetime] = None
    bio: Optional[str] = None
    experience_years: Optional[int] = None
    languages_spoken: Optional[str] = None
    education: Optional[str] = None
    address_line1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    mfa_enabled: bool = False
    last_login: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Success/Error responses
class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    error_code: Optional[str] = None


# Admin action responses
class AdminActionResponse(BaseModel):
    """Response for admin actions on users"""
    success: bool
    message: str
    action: str  # approve, reject, suspend, activate, delete
    user_id: int
    user_email: str
    user_name: str
    user_role: str
    performed_by: str  # admin email
    performed_at: datetime
    details: Optional[dict] = None


# Registration responses
class RegistrationResponse(BaseModel):
    """Enhanced registration response"""
    success: bool
    message: str
    user: UserResponse
    next_steps: list[str]
    requires_verification: bool = True
    requires_admin_approval: bool = False
