"""
Celery tasks for background processing
"""
from typing import Dict, Any, Optional
import asyncio
from celery import shared_task

from app.core.logging import get_logger
from app.services.email_service import get_email_service

logger = get_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(
    self,
    to_email: str,
    subject: str,
    html_content: str,
    plain_content: Optional[str] = None,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
    metadata: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Send an email via Celery task
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email body
        plain_content: Plain text email body (optional)
        from_email: Sender email (optional)
        from_name: Sender name (optional)
        metadata: Custom metadata for tracking (optional)
        
    Returns:
        Dictionary with send result
    """
    try:
        email_service = get_email_service()
        
        # Run async function in sync context
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            email_service.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                plain_content=plain_content,
                from_email=from_email,
                from_name=from_name,
                metadata=metadata
            )
        )
        
        if result["success"]:
            logger.info(f"Email sent successfully to {to_email}")
            return result
        else:
            logger.error(f"Failed to send email to {to_email}: {result.get('error')}")
            raise Exception(result.get("error", "Unknown error"))
            
    except Exception as exc:
        logger.error(f"Email task failed: {str(exc)}")
        # Retry the task
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_appointment_confirmation_task(
    self,
    to_email: str,
    patient_name: str,
    doctor_name: str,
    appointment_date: str,
    appointment_time: str,
    appointment_type: str,
    cancellation_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send appointment confirmation email via Celery
    
    Args:
        to_email: Patient email
        patient_name: Patient name
        doctor_name: Doctor name
        appointment_date: Appointment date
        appointment_time: Appointment time
        appointment_type: Type of appointment
        cancellation_url: URL for cancelling appointment
        
    Returns:
        Send result dictionary
    """
    try:
        email_service = get_email_service()
        
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            email_service.send_appointment_confirmation(
                to_email=to_email,
                patient_name=patient_name,
                doctor_name=doctor_name,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                appointment_type=appointment_type,
                cancellation_url=cancellation_url
            )
        )
        
        if result["success"]:
            logger.info(f"Appointment confirmation sent to {to_email}")
            return result
        else:
            raise Exception(result.get("error", "Unknown error"))
            
    except Exception as exc:
        logger.error(f"Appointment confirmation task failed: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_appointment_reminder_task(
    self,
    to_email: str,
    patient_name: str,
    doctor_name: str,
    appointment_date: str,
    appointment_time: str
) -> Dict[str, Any]:
    """
    Send appointment reminder email via Celery
    """
    try:
        email_service = get_email_service()
        
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            email_service.send_appointment_reminder(
                to_email=to_email,
                patient_name=patient_name,
                doctor_name=doctor_name,
                appointment_date=appointment_date,
                appointment_time=appointment_time
            )
        )
        
        if result["success"]:
            logger.info(f"Appointment reminder sent to {to_email}")
            return result
        else:
            raise Exception(result.get("error", "Unknown error"))
            
    except Exception as exc:
        logger.error(f"Appointment reminder task failed: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_task(
    self,
    to_email: str,
    first_name: str,
    reset_url: str,
    expiry_minutes: int = 15
) -> Dict[str, Any]:
    """
    Send password reset email via Celery
    """
    try:
        email_service = get_email_service()
        
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            email_service.send_password_reset(
                to_email=to_email,
                first_name=first_name,
                reset_url=reset_url,
                expiry_minutes=expiry_minutes
            )
        )
        
        if result["success"]:
            logger.info(f"Password reset email sent to {to_email}")
            return result
        else:
            raise Exception(result.get("error", "Unknown error"))
            
    except Exception as exc:
        logger.error(f"Password reset task failed: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task
def send_daily_appointment_reminders():
    """
    Scheduled task to send daily appointment reminders
    This should be scheduled to run daily via Celery Beat
    """
    from datetime import datetime, timedelta
    
    try:
        # TODO: Query appointments for tomorrow
        # For now, this is a placeholder
        tomorrow = datetime.now() + timedelta(days=1)
        
        logger.info(f"Sending appointment reminders for {tomorrow.date()}")
        
        # Example: Query from database and send reminders
        # appointments = get_appointments_for_date(tomorrow)
        # for appointment in appointments:
        #     send_appointment_reminder_task.delay(
        #         to_email=appointment.patient.email,
        #         patient_name=appointment.patient.name,
        #         doctor_name=appointment.doctor.name,
        #         appointment_date=appointment.date,
        #         appointment_time=appointment.time
        #     )
        
        return {"success": True, "message": "Daily reminders processed"}
        
    except Exception as exc:
        logger.error(f"Daily reminder task failed: {str(exc)}")
        raise


@shared_task
def cleanup_expired_tokens():
    """
    Scheduled task to clean up expired password reset tokens
    """
    try:
        # TODO: Implement token cleanup logic
        logger.info("Cleaning up expired tokens")
        
        return {"success": True, "message": "Token cleanup completed"}
        
    except Exception as exc:
        logger.error(f"Token cleanup task failed: {str(exc)}")
        raise
