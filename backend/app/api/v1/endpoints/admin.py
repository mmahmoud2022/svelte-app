"""
Admin endpoints for managing users, approving doctors, etc.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.blacklist import BlacklistReason
from app.schemas.auth import UserResponse, MessageResponse, AdminActionResponse
from app.core.logging import get_logger
from app.services.email_service import get_email_service
from app.services.blacklist_service import get_blacklist_service
from app.core.config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = get_logger(__name__)


# Pydantic schemas for request bodies
class SuspendUserRequest(BaseModel):
    """Request to suspend a user"""
    reason: str = "Suspended by admin"


class DeleteUserRequest(BaseModel):
    """Request to delete a user"""
    confirm: bool = True


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin role"""
    if current_user.role != UserRole.ADMIN:
        logger.warning(f"Non-admin user attempted admin action: user_id={current_user.id}, role={current_user.role}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Admin privileges required"
        )
    return current_user


@router.get("/doctors/pending", response_model=List[UserResponse])
async def get_pending_doctors(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    Get all doctors pending admin approval
    
    **Requires admin privileges**
    """
    logger.info(f"Admin {current_admin.email} requesting pending doctors list")
    
    pending_doctors = db.query(User).filter(
        User.role == UserRole.DOCTOR,
        User.admin_approved == False,
        User.is_active == True  # Only active accounts pending approval
    ).all()
    
    logger.info(f"Found {len(pending_doctors)} pending doctors")
    
    return [UserResponse.model_validate(doctor) for doctor in pending_doctors]


@router.post("/doctors/{doctor_id}/approve", response_model=AdminActionResponse)
async def approve_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    Approve a doctor account
    
    **Requires admin privileges**
    
    Returns detailed information about the approval action.
    """
    logger.info(f"Admin {current_admin.email} attempting to approve doctor_id={doctor_id}")
    
    # Find doctor
    doctor = db.query(User).filter(
        User.id == doctor_id,
        User.role == UserRole.DOCTOR
    ).first()
    
    if not doctor:
        logger.warning(f"Doctor not found: doctor_id={doctor_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    if doctor.admin_approved:
        logger.info(f"Doctor already approved: doctor_id={doctor_id}")
        return AdminActionResponse(
            success=True,
            message="Ce médecin est déjà approuvé",
            action="approve",
            user_id=doctor.id,
            user_email=doctor.email,
            user_name=f"Dr. {doctor.first_name} {doctor.last_name}",
            user_role=doctor.role.value,
            performed_by=current_admin.email,
            performed_at=datetime.utcnow(),
            details={"status": "already_approved"}
        )
    
    # Approve doctor
    doctor.admin_approved = True
    db.commit()
    
    logger.info(f"[ADMIN ACTION] Doctor approved | doctor_id={doctor_id} | email={doctor.email} | admin={current_admin.email}")
    
    # Send approval email
    email_service = get_email_service()
    email_sent = False
    
    try:
        await email_service.send_email(
            to_email=doctor.email,
            subject="Votre compte médecin a été approuvé - Santé",
            html_content=f"""
                <h2>Félicitations !</h2>
                <p>Bonjour Dr. {doctor.last_name},</p>
                <p>Nous avons le plaisir de vous informer que votre compte médecin a été approuvé par notre équipe.</p>
                <p>Vous pouvez maintenant vous connecter à votre compte et commencer à utiliser notre plateforme.</p>
                <p><a href="{settings.FRONTEND_URL}/login">Se connecter</a></p>
                <p>Bienvenue sur Santé !</p>
            """,
            metadata={"template": "doctor_approved", "user_id": str(doctor.id)}
        )
        logger.info(f"Approval email sent to {doctor.email}")
        email_sent = True
    except Exception as e:
        logger.error(f"Failed to send approval email: {str(e)}")
    
    return AdminActionResponse(
        success=True,
        message=f"Le compte du Dr. {doctor.last_name} a été approuvé avec succès",
        action="approve",
        user_id=doctor.id,
        user_email=doctor.email,
        user_name=f"Dr. {doctor.first_name} {doctor.last_name}",
        user_role=doctor.role.value,
        performed_by=current_admin.email,
        performed_at=datetime.utcnow(),
        details={
            "specialization": doctor.specialization,
            "email_sent": email_sent,
            "can_login": True
        }
    )


@router.post("/doctors/{doctor_id}/reject", response_model=AdminActionResponse)
async def reject_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    Reject a doctor account
    
    **Requires admin privileges**
    
    Returns detailed information about the rejection action.
    """
    logger.info(f"Admin {current_admin.email} attempting to reject doctor_id={doctor_id}")
    
    # Find doctor
    doctor = db.query(User).filter(
        User.id == doctor_id,
        User.role == UserRole.DOCTOR
    ).first()
    
    if not doctor:
        logger.warning(f"Doctor not found: doctor_id={doctor_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    # Store doctor info before deactivation
    doctor_name = f"Dr. {doctor.first_name} {doctor.last_name}"
    doctor_email = doctor.email
    
    # Deactivate doctor account
    doctor.is_active = False
    doctor.suspension_reason = "Rejected by admin during approval process"
    db.commit()
    
    logger.info(f"[ADMIN ACTION] Doctor rejected | doctor_id={doctor_id} | email={doctor_email} | admin={current_admin.email}")
    
    # Send rejection email
    email_service = get_email_service()
    email_sent = False
    
    try:
        await email_service.send_email(
            to_email=doctor_email,
            subject="Mise à jour concernant votre demande de compte médecin - Santé",
            html_content=f"""
                <h2>Mise à jour de votre demande</h2>
                <p>Bonjour Dr. {doctor.last_name},</p>
                <p>Nous vous remercions de l'intérêt que vous portez à notre plateforme.</p>
                <p>Après examen de votre dossier, nous ne sommes pas en mesure d'approuver votre compte pour le moment.</p>
                <p>Si vous pensez qu'il s'agit d'une erreur ou si vous souhaitez obtenir plus d'informations, n'hésitez pas à nous contacter.</p>
                <p>Cordialement,<br>L'équipe Santé</p>
            """,
            metadata={"template": "doctor_rejected", "user_id": str(doctor.id)}
        )
        logger.info(f"Rejection email sent to {doctor_email}")
        email_sent = True
    except Exception as e:
        logger.error(f"Failed to send rejection email: {str(e)}")
    
    return AdminActionResponse(
        success=True,
        message=f"Le compte du Dr. {doctor.last_name} a été rejeté",
        action="reject",
        user_id=doctor.id,
        user_email=doctor_email,
        user_name=doctor_name,
        user_role=doctor.role.value,
        performed_by=current_admin.email,
        performed_at=datetime.utcnow(),
        details={
            "account_deactivated": True,
            "email_sent": email_sent,
            "reason": "Rejected by admin during approval process"
        }
    )


@router.get("/doctors/all", response_model=List[UserResponse])
async def get_all_doctors(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    Get all doctors (approved and pending)
    
    **Requires admin privileges**
    """
    logger.info(f"Admin {current_admin.email} requesting all doctors list")
    
    all_doctors = db.query(User).filter(User.role == UserRole.DOCTOR).all()
    
    logger.info(f"Found {len(all_doctors)} doctors total")
    
    return [UserResponse.model_validate(doctor) for doctor in all_doctors]


# ============================================
# ENDPOINTS POUR GESTION DES UTILISATEURS
# ============================================

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    role: Optional[str] = Query(None, description="Filter by role: patient, doctor, admin"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    admin_approved: Optional[bool] = Query(None, description="Filter by admin approval status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    List all users with optional filters
    
    **Requires admin privileges**
    
    **Query Parameters:**
    - role: Filter by user role (patient, doctor, admin)
    - is_active: Filter by active status
    - is_verified: Filter by email verification status
    - admin_approved: Filter by admin approval status (for doctors)
    - skip: Pagination - number of records to skip
    - limit: Pagination - maximum number of records (default 100, max 500)
    """
    logger.info(f"Admin {current_admin.email} listing users with filters: role={role}, is_active={is_active}, is_verified={is_verified}")
    
    # Build query with filters
    query = db.query(User)
    
    if role:
        try:
            user_role = UserRole(role.lower())
            query = query.filter(User.role == user_role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {role}. Valid values: patient, doctor, admin"
            )
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)
    
    if admin_approved is not None:
        query = query.filter(User.admin_approved == admin_approved)
    
    # Apply pagination
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    logger.info(f"Found {len(users)} users (total: {total})")
    
    return [UserResponse.model_validate(user) for user in users]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    Get detailed information about a specific user
    
    **Requires admin privileges**
    """
    logger.info(f"Admin {current_admin.email} requesting details for user_id={user_id}")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        logger.warning(f"User not found: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)


@router.post("/users/{user_id}/suspend", response_model=AdminActionResponse)
async def suspend_user(
    user_id: int,
    suspend_data: SuspendUserRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    Suspend a user account (doctor or patient)
    
    **Requires admin privileges**
    
    This will:
    - Set is_active to False
    - Add email to blacklist
    - Set suspension_reason
    - Revoke all active tokens
    - Send notification email to the user
    
    Returns detailed information about the suspension action.
    """
    logger.info(f"Admin {current_admin.email} attempting to suspend user_id={user_id}")
    
    # Find user
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        logger.warning(f"User not found: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent suspending admin accounts
    if user.role == UserRole.ADMIN:
        logger.warning(f"Attempt to suspend admin account: user_id={user_id}, by={current_admin.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot suspend admin accounts"
        )
    
    # Prevent suspending self
    if user.id == current_admin.id:
        logger.warning(f"Admin attempted to suspend themselves: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot suspend your own account"
        )
    
    # Check if already suspended
    if not user.is_active:
        logger.info(f"User already suspended: user_id={user_id}")
        return AdminActionResponse(
            success=True,
            message="Ce compte est déjà suspendu",
            action="suspend",
            user_id=user.id,
            user_email=user.email,
            user_name=f"{user.first_name} {user.last_name}",
            user_role=user.role.value,
            performed_by=current_admin.email,
            performed_at=datetime.utcnow(),
            details={"status": "already_suspended", "reason": user.suspension_reason}
        )
    
    # Suspend user
    user.is_active = False
    user.suspension_reason = suspend_data.reason
    
    # Add email to blacklist
    blacklist_service = get_blacklist_service()
    blacklist_service.add_to_blacklist(
        email=user.email,
        reason=BlacklistReason.SUSPENDED,
        details=suspend_data.reason,
        original_user_id=user.id,
        original_user_name=f"{user.first_name} {user.last_name}",
        original_user_role=user.role.value,
        admin_id=current_admin.id,
        admin_email=current_admin.email,
        db=db
    )
    
    # Revoke all tokens
    from app.services.auth_service import AuthService
    auth_service = AuthService()
    auth_service.revoke_all_user_tokens(user.id, db)
    
    db.commit()
    
    logger.info(
        f"[ADMIN ACTION] User suspended | "
        f"user_id={user_id} | "
        f"email={user.email} | "
        f"role={user.role.value} | "
        f"reason={suspend_data.reason} | "
        f"admin_email={current_admin.email}"
    )
    
    # Send notification email
    email_service = get_email_service()
    email_sent = False
    
    try:
        role_label = "patient" if user.role == UserRole.PATIENT else "médecin"
        await email_service.send_email(
            to_email=user.email,
            subject="Suspension de votre compte - Santé",
            html_content=f"""
                <h2>Suspension de compte</h2>
                <p>Bonjour {user.first_name} {user.last_name},</p>
                <p>Nous vous informons que votre compte {role_label} a été suspendu.</p>
                <p><strong>Raison :</strong> {suspend_data.reason}</p>
                <p>Si vous pensez qu'il s'agit d'une erreur ou si vous souhaitez obtenir plus d'informations, 
                veuillez contacter notre équipe de support.</p>
                <p>Cordialement,<br>L'équipe Santé</p>
            """,
            metadata={"template": "account_suspended", "user_id": str(user.id)}
        )
        logger.info(f"Suspension email sent to {user.email}")
        email_sent = True
    except Exception as e:
        logger.error(f"Failed to send suspension email: {str(e)}")
    
    return AdminActionResponse(
        success=True,
        message=f"Le compte de {user.first_name} {user.last_name} a été suspendu",
        action="suspend",
        user_id=user.id,
        user_email=user.email,
        user_name=f"{user.first_name} {user.last_name}",
        user_role=user.role.value,
        performed_by=current_admin.email,
        performed_at=datetime.utcnow(),
        details={
            "reason": suspend_data.reason,
            "tokens_revoked": True,
            "added_to_blacklist": True,
            "email_sent": email_sent,
            "can_login": False
        }
    )


@router.post("/users/{user_id}/activate", response_model=AdminActionResponse)
async def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    Reactivate a suspended user account
    
    **Requires admin privileges**
    
    This will:
    - Set is_active to True
    - Remove email from blacklist
    - Clear suspension_reason
    - Send notification email to the user
    
    Returns detailed information about the activation action.
    """
    logger.info(f"Admin {current_admin.email} attempting to activate user_id={user_id}")
    
    # Find user
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        logger.warning(f"User not found: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already active
    if user.is_active:
        logger.info(f"User already active: user_id={user_id}")
        return AdminActionResponse(
            success=True,
            message="Ce compte est déjà actif",
            action="activate",
            user_id=user.id,
            user_email=user.email,
            user_name=f"{user.first_name} {user.last_name}",
            user_role=user.role.value,
            performed_by=current_admin.email,
            performed_at=datetime.utcnow(),
            details={"status": "already_active"}
        )
    
    # Reactivate user
    user.is_active = True
    user.suspension_reason = None
    
    # Remove email from blacklist
    blacklist_service = get_blacklist_service()
    blacklist_service.remove_from_blacklist(user.email, db)
    
    db.commit()
    
    logger.info(
        f"[ADMIN ACTION] User reactivated | "
        f"user_id={user_id} | "
        f"email={user.email} | "
        f"role={user.role.value} | "
        f"admin_email={current_admin.email}"
    )
    
    # Send notification email
    email_service = get_email_service()
    
    try:
        role_label = "patient" if user.role == UserRole.PATIENT else "médecin"
        await email_service.send_email(
            to_email=user.email,
            subject="Réactivation de votre compte - Santé",
            html_content=f"""
                <h2>Compte réactivé</h2>
                <p>Bonjour {user.first_name} {user.last_name},</p>
                <p>Nous vous informons que votre compte {role_label} a été réactivé.</p>
                <p>Vous pouvez maintenant vous reconnecter à notre plateforme.</p>
                <p><a href="{settings.FRONTEND_URL}/login">Se connecter</a></p>
                <p>Bienvenue de nouveau sur Santé !</p>
            """,
            metadata={"template": "account_reactivated", "user_id": str(user.id)}
        )
        logger.info(f"Reactivation email sent to {user.email}")
        email_sent = True
    except Exception as e:
        logger.error(f"Failed to send reactivation email: {str(e)}")
    
    return AdminActionResponse(
        success=True,
        message=f"Le compte de {user.first_name} {user.last_name} a été réactivé avec succès",
        action="activate",
        user_id=user.id,
        user_email=user.email,
        user_name=f"{user.first_name} {user.last_name}",
        user_role=user.role.value,
        performed_by=current_admin.email,
        performed_at=datetime.utcnow(),
        details={
            "removed_from_blacklist": True,
            "suspension_reason_cleared": True,
            "email_sent": email_sent,
            "can_login": True
        }
    )


@router.delete("/users/{user_id}", response_model=AdminActionResponse)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    Delete a user account permanently (doctor or patient)
    
    **Requires admin privileges**
    
    This will:
    - Add email to blacklist permanently
    - Delete all user tokens
    - Permanently delete the user from database
    - Send notification email (if configured)
    
    Returns detailed information about the deletion action.
    
    ⚠️ WARNING: This is a permanent action and cannot be undone!
    
    This will:
    - Permanently delete the user from the database
    - Revoke all tokens
    - Delete associated data (based on your data retention policy)
    
    Note: For GDPR compliance, consider implementing soft delete or data anonymization
    instead of hard delete.
    """
    logger.info(f"Admin {current_admin.email} attempting to delete user_id={user_id}")
    
    # Find user
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        logger.warning(f"User not found: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting admin accounts
    if user.role == UserRole.ADMIN:
        logger.warning(f"Attempt to delete admin account: user_id={user_id}, by={current_admin.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete admin accounts"
        )
    
    # Prevent deleting self
    if user.id == current_admin.id:
        logger.warning(f"Admin attempted to delete themselves: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete your own account"
        )
    
    # Store user info for logging and email
    user_email = user.email
    user_name = f"{user.first_name} {user.last_name}"
    user_role = user.role
    
    # Add email to blacklist BEFORE deleting user
    blacklist_service = get_blacklist_service()
    blacklist_service.add_to_blacklist(
        email=user.email,
        reason=BlacklistReason.DELETED,
        details="Account permanently deleted by admin",
        original_user_id=user.id,
        original_user_name=user_name,
        original_user_role=user.role.value,
        admin_id=current_admin.id,
        admin_email=current_admin.email,
        db=db
    )
    
    # Revoke all tokens before deletion
    from app.services.auth_service import AuthService
    from app.models.auth import RefreshToken, VerificationToken
    
    auth_service = AuthService()
    
    # Delete all verification tokens
    db.query(VerificationToken).filter(VerificationToken.user_id == user.id).delete()
    
    # Delete all refresh tokens
    db.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()
    
    # Delete user
    db.delete(user)
    db.commit()
    
    logger.info(
        f"[ADMIN ACTION] User deleted | "
        f"user_id={user_id} | "
        f"email={user_email} | "
        f"role={user_role.value} | "
        f"admin_email={current_admin.email}"
    )
    
    # Send notification email (if needed for records)
    email_service = get_email_service()
    email_sent = False
    
    try:
        role_label = "patient" if user_role == UserRole.PATIENT else "médecin"
        await email_service.send_email(
            to_email=user_email,
            subject="Suppression de votre compte - Santé",
            html_content=f"""
                <h2>Suppression de compte</h2>
                <p>Bonjour {user_name},</p>
                <p>Nous vous confirmons que votre compte {role_label} a été supprimé de notre plateforme.</p>
                <p>Toutes vos données personnelles ont été supprimées conformément à notre politique de confidentialité.</p>
                <p>Si vous n'êtes pas à l'origine de cette action ou si vous avez des questions, 
                veuillez contacter notre équipe de support.</p>
                <p>Cordialement,<br>L'équipe Santé</p>
            """,
            metadata={"template": "account_deleted", "user_email": user_email}
        )
        logger.info(f"Deletion confirmation email sent to {user_email}")
        email_sent = True
    except Exception as e:
        logger.error(f"Failed to send deletion email: {str(e)}")
    
    return AdminActionResponse(
        success=True,
        message=f"Le compte de {user_name} a été supprimé définitivement",
        action="delete",
        user_id=user_id,
        user_email=user_email,
        user_name=user_name,
        user_role=user_role.value,
        performed_by=current_admin.email,
        performed_at=datetime.utcnow(),
        details={
            "permanently_deleted": True,
            "added_to_blacklist": True,
            "tokens_deleted": True,
            "email_sent": email_sent,
            "can_recreate_account": False
        }
    )


@router.get("/patients", response_model=List[UserResponse])
async def list_patients(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    List all patients with optional filters
    
    **Requires admin privileges**
    """
    logger.info(f"Admin {current_admin.email} listing patients")
    
    query = db.query(User).filter(User.role == UserRole.PATIENT)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)
    
    total = query.count()
    patients = query.offset(skip).limit(limit).all()
    
    logger.info(f"Found {len(patients)} patients (total: {total})")
    
    return [UserResponse.model_validate(patient) for patient in patients]
