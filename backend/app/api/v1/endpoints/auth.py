"""
Authentication endpoints for registration, login, password reset, and verification
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.core.dependencies import get_current_user, get_current_verified_user
from app.services.auth_service import AuthService, get_auth_service
from app.services.email_service import get_email_service
from app.services.blacklist_service import get_blacklist_service
from app.models.user import User, UserRole
from app.schemas.auth import (
    PatientRegister,
    PractitionerRegister,
    AdminRegister,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    TokenResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChange,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    UserResponse,
    MessageResponse,
    RegistrationResponse,
)
from app.core.logging import get_logger

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger(__name__)


# Helper function to get client info
def get_client_info(request: Request) -> dict:
    """Extract client information from request"""
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent")
    }


@router.get("/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """
    Get public statistics about the platform
    No authentication required
    """
    try:
        # Total users
        total_users = db.query(User).count()
        
        # Total doctors
        total_doctors = db.query(User).filter(User.role == UserRole.DOCTOR).count()
        
        # Total patients
        total_patients = db.query(User).filter(User.role == UserRole.PATIENT).count()
        
        # Pending doctors (not yet approved)
        pending_doctors = db.query(User).filter(
            User.role == UserRole.DOCTOR,
            User.admin_approved == False
        ).count()
        
        # Active users (email verified and not suspended)
        active_users = db.query(User).filter(
            User.is_active == True,
            User.is_verified == True
        ).count()
        
        logger.info(f"[ACTION] | action=statistics_fetched | total_users={total_users} | total_doctors={total_doctors} | total_patients={total_patients}")
        
        return {
            "total_users": total_users,
            "total_doctors": total_doctors,
            "total_patients": total_patients,
            "pending_doctors": pending_doctors,
            "active_users": active_users
        }
    except Exception as e:
        logger.error(f"[ERROR] | action=statistics_fetch_failed | error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch statistics"
        )


@router.post("/register/patient", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_patient(
    patient_data: PatientRegister,
    request: Request,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new patient
    
    - **email**: Valid email address
    - **password**: Strong password (min 8 chars, uppercase, lowercase, number)
    - **first_name**: Patient's first name
    - **last_name**: Patient's last name
    
    Returns detailed registration information with next steps.
    """
    logger.info(
        f"[PATIENT REGISTRATION] Attempt started | "
        f"email={patient_data.email} | "
        f"ip={request.client.host if request.client else 'unknown'} | "
        f"name={patient_data.first_name} {patient_data.last_name}"
    )
    
    # Check if email is blacklisted
    blacklist_service = get_blacklist_service()
    is_blacklisted, blacklist_entry = blacklist_service.is_blacklisted(patient_data.email, db)
    
    if is_blacklisted:
        logger.warning(
            f"[PATIENT REGISTRATION] Blacklisted email attempt | "
            f"email={patient_data.email} | "
            f"reason={blacklist_entry.reason.value} | "
            f"ip={request.client.host if request.client else 'unknown'}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=blacklist_service.get_blacklist_message(blacklist_entry)
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == patient_data.email).first()
    if existing_user:
        logger.warning(
            f"[PATIENT REGISTRATION] Failed - Email already exists | "
            f"email={patient_data.email} | "
            f"existing_user_id={existing_user.id} | "
            f"existing_user_role={existing_user.role.value}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new patient user
    hashed_password = auth_service.hash_password(patient_data.password)
    
    new_user = User(
        email=patient_data.email,
        hashed_password=hashed_password,
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        phone=patient_data.phone,
        date_of_birth=patient_data.date_of_birth,
        gender=patient_data.gender,
        emergency_contact_name=patient_data.emergency_contact_name,
        emergency_contact_phone=patient_data.emergency_contact_phone,
        emergency_contact_relationship=patient_data.emergency_contact_relationship,
        role=UserRole.PATIENT,
        is_active=True,
        is_verified=False,
        admin_approved=True,  # Patients are auto-approved
        marketing_consent=patient_data.marketing_consent,
        data_processing_consent=True,
        terms_accepted_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"Patient user created: user_id={new_user.id}, email={new_user.email}")
    
    # Generate verification token
    verification_token = auth_service.generate_verification_token(
        user_id=new_user.id,
        token_type="email_verification",
        db=db,
        expires_in_hours=24
    )
    
    # Send verification email
    email_service = get_email_service()
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
    
    try:
        await email_service.send_email(
            to_email=new_user.email,
            subject="Vérifiez votre adresse email - Santé",
            html_content=f"""
                <h2>Bienvenue sur Santé !</h2>
                <p>Bonjour {new_user.first_name},</p>
                <p>Merci de vous être inscrit. Pour activer votre compte, veuillez cliquer sur le lien ci-dessous :</p>
                <p><a href="{verification_url}">Vérifier mon email</a></p>
                <p>Ce lien est valable pendant 24 heures.</p>
            """,
            metadata={"template": "email_verification", "user_id": str(new_user.id)}
        )
        logger.info(f"Verification email sent to {new_user.email}")
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
        # Don't fail registration if email fails
    
    logger.info(
        f"[PATIENT REGISTRATION] Success | "
        f"user_id={new_user.id} | "
        f"email={new_user.email} | "
        f"name={new_user.first_name} {new_user.last_name} | "
        f"phone={new_user.phone}"
    )
    
    return RegistrationResponse(
        success=True,
        message="Inscription réussie ! Veuillez vérifier votre email pour activer votre compte.",
        user=UserResponse.model_validate(new_user),
        next_steps=[
            "Consultez votre boîte email et cliquez sur le lien de vérification",
            "Le lien de vérification est valable pendant 24 heures",
            "Une fois votre email vérifié, vous pourrez vous connecter",
            "Si vous ne recevez pas l'email, vérifiez vos spams"
        ],
        requires_verification=True,
        requires_admin_approval=False
    )


@router.post("/register/doctor", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_practitioner(
    practitioner_data: PractitionerRegister,
    request: Request,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new practitioner/doctor
    
    Returns detailed registration information with next steps including admin approval requirement.
    
    Requires additional professional information:
    - **specialization**: Medical specialization
    """
    from datetime import datetime
    
    logger.info(
        f"[DOCTOR REGISTRATION] Attempt started | "
        f"email={practitioner_data.email} | "
        f"ip={request.client.host if request.client else 'unknown'} | "
        f"name=Dr. {practitioner_data.first_name} {practitioner_data.last_name} | "
        f"specialization={practitioner_data.specialization}"
    )
    
    # Check if email is blacklisted
    blacklist_service = get_blacklist_service()
    is_blacklisted, blacklist_entry = blacklist_service.is_blacklisted(practitioner_data.email, db)
    
    if is_blacklisted:
        logger.warning(
            f"[DOCTOR REGISTRATION] Blacklisted email attempt | "
            f"email={practitioner_data.email} | "
            f"reason={blacklist_entry.reason.value} | "
            f"ip={request.client.host if request.client else 'unknown'}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=blacklist_service.get_blacklist_message(blacklist_entry)
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == practitioner_data.email).first()
    if existing_user:
        logger.warning(
            f"[DOCTOR REGISTRATION] Failed - Email already exists | "
            f"email={practitioner_data.email} | "
            f"existing_user_id={existing_user.id} | "
            f"existing_user_role={existing_user.role.value}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if license number is already used
    # existing_license = db.query(User).filter(
    #     User.license_number == practitioner_data.license_number,
    #     User.role == UserRole.DOCTOR
    # ).first()
    # if existing_license:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="License number already registered"
    #     )
    
    # Create new practitioner user
    hashed_password = auth_service.hash_password(practitioner_data.password)
    
    new_user = User(
        email=practitioner_data.email,
        hashed_password=hashed_password,
        first_name=practitioner_data.first_name,
        last_name=practitioner_data.last_name,
        gender=practitioner_data.gender,
        phone=practitioner_data.phone,
        role=UserRole.DOCTOR,
        is_active=True,
        is_verified=False,  # Require email verification
        admin_approved=False,  # Require admin approval
        specialization=practitioner_data.specialization,
        #license_number=practitioner_data.license_number,
        bio=practitioner_data.bio,
        consultation_fee=practitioner_data.consultation_fee,
        languages_spoken=practitioner_data.languages_spoken,
        accepting_new_patients=True,
        data_processing_consent=True,
        terms_accepted_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create DoctorProfile automatically with default values
    from app.models.doctor import DoctorProfile, DoctorSettings, SpecialtyEnum, ConsultationTypeEnum
    
    # Map string specialization to enum (default to OTHER if not found)
    specialty_map = {
        'general_practitioner': SpecialtyEnum.GENERAL_PRACTITIONER,
        'cardiologist': SpecialtyEnum.CARDIOLOGIST,
        'dermatologist': SpecialtyEnum.DERMATOLOGIST,
        'pediatrician': SpecialtyEnum.PEDIATRICIAN,
        'gynecologist': SpecialtyEnum.GYNECOLOGIST,
        'psychiatrist': SpecialtyEnum.PSYCHIATRIST,
        'ophthalmologist': SpecialtyEnum.OPHTHALMOLOGIST,
        'dentist': SpecialtyEnum.DENTIST,
        'orthopedist': SpecialtyEnum.ORTHOPEDIST,
        'neurologist': SpecialtyEnum.NEUROLOGIST,
        'radiologist': SpecialtyEnum.RADIOLOGIST,
        'surgeon': SpecialtyEnum.SURGEON,
    }
    specialty_enum = specialty_map.get(practitioner_data.specialization.lower(), SpecialtyEnum.OTHER)
    
    doctor_profile = DoctorProfile(
        user_id=new_user.id,
        specialty=specialty_enum,
        rpps_number=None,  # No RPPS number by default - doctor can update it later
        biography=practitioner_data.bio or "",
        languages=practitioner_data.languages_spoken.split(',') if practitioner_data.languages_spoken else ["Français"],
        education=[],
        experience_years=0,
        consultation_types=ConsultationTypeEnum.BOTH,
        consultation_duration=30,
        consultation_price=float(practitioner_data.consultation_fee / 100) if practitioner_data.consultation_fee else 50.0,
        accepts_new_patients=True,
        is_public=False,  # Not public until profile is completed
        is_verified=False
    )
    db.add(doctor_profile)
    db.commit()
    db.refresh(doctor_profile)
    
    # Create default settings for the doctor
    settings = DoctorSettings(doctor_id=doctor_profile.id)
    db.add(settings)
    db.commit()
    
    # Generate verification token
    verification_token = auth_service.generate_verification_token(
        user_id=new_user.id,
        token_type="email_verification",
        db=db,
        expires_in_hours=24
    )
    
    # Send verification email
    email_service = get_email_service()
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
    
    try:
        await email_service.send_email(
            to_email=new_user.email,
            subject="Vérifiez votre compte praticien - Santé",
            html_content=f"""
                <h2>Bienvenue sur Santé !</h2>
                <p>Bonjour Dr. {new_user.last_name},</p>
                <p>Merci de vous être inscrit en tant que praticien. Pour activer votre compte, veuillez cliquer sur le lien ci-dessous :</p>
                <p><a href="{verification_url}">Vérifier mon email</a></p>
                <p>Ce lien est valable pendant 24 heures.</p>
                <p><strong>Note importante :</strong> Après la vérification de votre email, votre profil devra être validé par un administrateur avant que vous puissiez vous connecter. Vous recevrez un email de confirmation une fois votre compte approuvé.</p>
                <p>Cette étape de validation nous permet de garantir la qualité et la sécurité de notre plateforme.</p>
            """,
            metadata={"template": "email_verification", "user_id": str(new_user.id)}
        )
        logger.info(f"Verification email sent to {new_user.email}")
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
    
    logger.info(
        f"[DOCTOR REGISTRATION] Success | "
        f"user_id={new_user.id} | "
        f"email={new_user.email} | "
        f"name=Dr. {new_user.first_name} {new_user.last_name} | "
        f"specialization={new_user.specialization} | "
        f"admin_approved={new_user.admin_approved}"
    )
    
    return RegistrationResponse(
        success=True,
        message="Inscription réussie ! Veuillez vérifier votre email et attendre la validation admin.",
        user=UserResponse.model_validate(new_user),
        next_steps=[
            "Consultez votre boîte email et cliquez sur le lien de vérification",
            "Le lien de vérification est valable pendant 24 heures",
            "Après vérification, votre compte sera examiné par un administrateur",
            "Vous recevrez un email de confirmation une fois votre compte approuvé par l'admin",
            "La validation admin peut prendre de 24 à 48 heures"
        ],
        requires_verification=True,
        requires_admin_approval=True
    )


@router.post("/register/admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_admin(
    admin_data: AdminRegister,
    request: Request,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new administrator
    
    **Requires admin secret for security**
    """
    from datetime import datetime
    
    # Verify admin secret
    if admin_data.admin_secret != settings.ADMIN_SECRET:
        logger.warning(f"Failed admin registration attempt from {request.client.host if request.client else 'unknown'}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin secret"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == admin_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new admin user
    hashed_password = auth_service.hash_password(admin_data.password)
    
    new_user = User(
        email=admin_data.email,
        hashed_password=hashed_password,
        first_name=admin_data.first_name,
        last_name=admin_data.last_name,
        phone=admin_data.phone,
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,  # Admins are auto-verified
        admin_approved=True,  # Admins are auto-approved
        data_processing_consent=True,
        terms_accepted_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New admin registered: {new_user.email}")
    
    return UserResponse.model_validate(new_user)


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login with email and password
    
    Returns access token and refresh token
    """
    from datetime import datetime, timedelta
    
    client_info = get_client_info(request)
    logger.info(
        f"[LOGIN] Attempt started | "
        f"email={login_data.email} | "
        f"ip={client_info.get('ip_address', 'unknown')} | "
        f"user_agent={client_info.get('user_agent', 'unknown')[:100]}"
    )
    
    # Check if email is blacklisted
    blacklist_service = get_blacklist_service()
    is_blacklisted, blacklist_entry = blacklist_service.is_blacklisted(login_data.email, db)
    
    if is_blacklisted:
        logger.warning(
            f"[LOGIN] Blacklisted email attempt | "
            f"email={login_data.email} | "
            f"reason={blacklist_entry.reason.value} | "
            f"ip={client_info.get('ip_address', 'unknown')}"
        )
        auth_service.log_login_attempt(
            email=login_data.email,
            success=False,
            db=db,
            failure_reason=f"Blacklisted - {blacklist_entry.reason.value}",
            **client_info
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=blacklist_service.get_blacklist_message(blacklist_entry)
        )
    
    # Check for too many failed attempts
    if auth_service.check_login_attempts(login_data.email, db):
        logger.warning(
            f"[LOGIN] Rate limited | "
            f"email={login_data.email} | "
            f"ip={client_info.get('ip_address', 'unknown')}"
        )
        auth_service.log_login_attempt(
            email=login_data.email,
            success=False,
            db=db,
            failure_reason="Too many failed attempts",
            **client_info
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again later."
        )
    
    # Check if user exists and password is correct before checking approval status
    user_check = db.query(User).filter(User.email == login_data.email).first()
    
    if user_check and user_check.role == UserRole.DOCTOR:
        # Verify password
        if auth_service.verify_password(login_data.password, user_check.hashed_password):
            # Check if doctor is pending admin approval
            if not user_check.admin_approved:
                logger.info(f"Login attempt for unapproved doctor: email={login_data.email}, user_id={user_check.id}")
                auth_service.log_login_attempt(
                    email=login_data.email,
                    success=False,
                    db=db,
                    failure_reason="Pending admin approval",
                    **client_info
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Votre compte médecin est en attente de validation par un administrateur. Vous recevrez un email une fois votre compte approuvé."
                )
    
    # Authenticate user
    user = auth_service.authenticate_user(login_data.email, login_data.password, db)
    
    if not user:
        auth_service.log_login_attempt(
            email=login_data.email,
            success=False,
            db=db,
            failure_reason="Invalid credentials",
            **client_info
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role.value}
    )
    
    # Create refresh token
    refresh_token = auth_service.create_refresh_token(
        user_id=user.id,
        db=db,
        device_id=login_data.device_id,
        remember_me=login_data.remember_me,
        **client_info
    )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Log successful login
    auth_service.log_login_attempt(
        email=login_data.email,
        success=True,
        db=db,
        **client_info
    )
    
    logger.info(
        f"[LOGIN] Success | "
        f"user_id={user.id} | "
        f"email={user.email} | "
        f"role={user.role.value} | "
        f"ip={client_info.get('ip_address', 'unknown')}"
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Refresh access token using refresh token
    """
    from app.models.auth import RefreshToken
    
    # Find refresh token
    refresh_token_obj = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_data.refresh_token
    ).first()
    
    if not refresh_token_obj or not refresh_token_obj.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user
    user = db.query(User).filter(User.id == refresh_token_obj.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    access_token = auth_service.create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role.value}
    )
    
    # Update last used
    from datetime import datetime
    refresh_token_obj.last_used_at = datetime.utcnow()
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_data.refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout")
async def logout(
    refresh_data: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logout and revoke refresh token
    """
    auth_service.revoke_refresh_token(refresh_data.refresh_token, db)
    logger.info(f"User logged out: {current_user.email}")
    
    return MessageResponse(message="Successfully logged out")


@router.post("/logout-all")
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logout from all devices by revoking all refresh tokens
    """
    auth_service.revoke_all_user_tokens(current_user.id, db)
    logger.info(f"User logged out from all devices: {current_user.email}")
    
    return MessageResponse(message="Successfully logged out from all devices")


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    verification_data: EmailVerificationConfirm,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Verify email address with token
    """
    logger.info(f"Email verification attempt: token={verification_data.token[:10]}...")
    
    # Verify token
    token = auth_service.verify_verification_token(
        token=verification_data.token,
        token_type="email_verification",
        db=db
    )
    
    if not token:
        logger.warning(f"Email verification failed: Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Get user
    user = db.query(User).filter(User.id == token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Mark user as verified
    user.is_verified = True
    
    # Mark token as used
    auth_service.mark_token_as_used(token, db)
    
    db.commit()
    
    logger.info(f"Email verified successfully: user_id={user.id}, email={user.email}")
    
    return MessageResponse(
        message="Email verified successfully. You can now login.",
        success=True
    )


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    email_data: EmailVerificationRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Resend verification email
    """
    # Find user
    user = db.query(User).filter(User.email == email_data.email).first()
    if not user:
        # Don't reveal if user exists
        return MessageResponse(
            message="If the email exists, a verification link has been sent.",
            success=True
        )
    
    if user.is_verified:
        return MessageResponse(
            message="Email is already verified.",
            success=True
        )
    
    # Generate new verification token
    verification_token = auth_service.generate_verification_token(
        user_id=user.id,
        token_type="email_verification",
        db=db,
        expires_in_hours=24
    )
    
    # Send verification email
    email_service = get_email_service()
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
    
    try:
        await email_service.send_email(
            to_email=user.email,
            subject="Vérifiez votre adresse email - Santé",
            html_content=f"""
                <h2>Vérifiez votre email</h2>
                <p>Bonjour {user.first_name},</p>
                <p>Cliquez sur le lien ci-dessous pour vérifier votre adresse email :</p>
                <p><a href="{verification_url}">Vérifier mon email</a></p>
                <p>Ce lien est valable pendant 24 heures.</p>
            """,
            metadata={"template": "email_verification", "user_id": str(user.id)}
        )
    except Exception as e:
        logger.error(f"Failed to resend verification email: {str(e)}")
    
    return MessageResponse(
        message="Verification email sent successfully.",
        success=True
    )


@router.post("/request-password-reset", response_model=MessageResponse)
async def request_password_reset(
    reset_data: PasswordResetRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Request password reset
    
    Sends reset link to user's email
    """
    logger.info(f"Password reset requested: email={reset_data.email}")
    
    # Find user
    user = db.query(User).filter(User.email == reset_data.email).first()
    if not user:
        # Don't reveal if user exists
        logger.info(f"Password reset requested for non-existent user: email={reset_data.email}")
        return MessageResponse(
            message="If the email exists, a password reset link has been sent.",
            success=True
        )
    
    # Generate reset token
    reset_token = auth_service.generate_verification_token(
        user_id=user.id,
        token_type="password_reset",
        db=db,
        expires_in_hours=1  # 1 hour for password reset
    )
    
    # Send reset email
    email_service = get_email_service()
    
    try:
        await email_service.send_password_reset(
            to_email=user.email,
            first_name=user.first_name,
            reset_url=f"{settings.FRONTEND_URL}/reset-password?token={reset_token}",
            expiry_minutes=60
        )
        logger.info(f"Password reset email sent: user_id={user.id}, email={user.email}")
    except Exception as e:
        logger.error(f"Failed to send password reset email: user_id={user.id}, email={user.email}, error={str(e)}")
    
    return MessageResponse(
        message="If the email exists, a password reset link has been sent.",
        success=True
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Reset password with token
    """
    logger.info(f"Password reset confirmation attempt: token={reset_data.token[:10]}...")
    
    # Verify token
    token = auth_service.verify_verification_token(
        token=reset_data.token,
        token_type="password_reset",
        db=db
    )
    
    if not token:
        logger.warning(f"Password reset failed: Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Get user
    user = db.query(User).filter(User.id == token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.hashed_password = auth_service.hash_password(reset_data.new_password)
    
    # Mark token as used
    auth_service.mark_token_as_used(token, db)
    
    # Revoke all existing refresh tokens for security
    auth_service.revoke_all_user_tokens(user.id, db)
    
    db.commit()
    
    logger.info(f"Password reset successfully: user_id={user.id}, email={user.email}, all_tokens_revoked=True")
    
    return MessageResponse(
        message="Password reset successfully. Please login with your new password.",
        success=True
    )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Change password (when logged in)
    """
    # Verify current password
    if not auth_service.verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = auth_service.hash_password(password_data.new_password)
    
    # Revoke all other sessions for security
    auth_service.revoke_all_user_tokens(current_user.id, db)
    
    db.commit()
    
    logger.info(f"Password changed for user: {current_user.email}")
    
    return MessageResponse(
        message="Password changed successfully. Please login again.",
        success=True
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    """
    return UserResponse.model_validate(current_user)
