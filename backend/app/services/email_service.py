"""
Email Service with SMTP (Mailpit) and Amazon SES support
Handles sending emails with templates, retry logic, and delivery tracking
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class EmailService:
    """
    Email service for sending emails via SMTP (Mailpit) or Amazon SES
    
    Provider selection:
    - SMTP (Mailpit): For development and testing
    - Amazon SES: For production
    """
    
    def __init__(
        self,
        provider: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ):
        """
        Initialize email service
        
        Args:
            provider: Email provider ('smtp' or 'ses')
            from_email: Default sender email address
            from_name: Default sender name
        """
        self.provider = provider or settings.EMAIL_PROVIDER
        self.from_email = from_email or settings.EMAIL_FROM
        self.from_name = from_name or settings.EMAIL_FROM_NAME
        self.logger = logger
        
        # Initialize SES client if using AWS SES
        self.ses_client = None
        if self.provider == "ses":
            try:
                import boto3
                self.ses_client = boto3.client(
                    'ses',
                    region_name=settings.AWS_SES_REGION,
                    aws_access_key_id=settings.AWS_SES_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SES_SECRET_ACCESS_KEY
                )
                self.logger.info("Amazon SES client initialized successfully")
            except ImportError:
                self.logger.error("boto3 not installed. Install with: pip install boto3")
                raise
            except Exception as e:
                self.logger.error(f"Failed to initialize SES client: {str(e)}")
                raise
        else:
            self.logger.info(f"Email service initialized with SMTP provider (host: {settings.SMTP_HOST}:{settings.SMTP_PORT})")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, str]] = None,
        reply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            plain_content: Plain text email body (optional)
            from_email: Sender email (optional, uses default if not provided)
            from_name: Sender name (optional)
            attachments: List of attachments (optional)
            metadata: Custom metadata for tracking (optional)
            reply_to: Reply-to email address (optional)
            
        Returns:
            Dictionary with send result
        """
        from_email = from_email or self.from_email
        from_name = from_name or self.from_name
        
        if not settings.EMAIL_ENABLED:
            self.logger.warning("Email sending is disabled")
            return {
                "success": False,
                "error": "Email sending is disabled",
                "to_email": to_email
            }
        
        try:
            if self.provider == "ses":
                return await self._send_via_ses(
                    to_email, subject, html_content, plain_content,
                    from_email, from_name, reply_to, metadata
                )
            else:  # smtp
                return await self._send_via_smtp(
                    to_email, subject, html_content, plain_content,
                    from_email, from_name, reply_to, attachments
                )
                
        except Exception as e:
            self.logger.error(
                f"Failed to send email to {to_email}",
                extra={
                    "to_email": to_email,
                    "subject": subject,
                    "error": str(e),
                    "provider": self.provider
                }
            )
            return {
                "success": False,
                "error": str(e),
                "to_email": to_email
            }
    
    async def _send_via_ses(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str],
        from_email: str,
        from_name: str,
        reply_to: Optional[str],
        metadata: Optional[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Send email via Amazon SES
        
        Amazon SES is highly reliable and cost-effective for production
        """
        try:
            # Format sender with name
            sender = f"{from_name} <{from_email}>" if from_name else from_email
            
            # Prepare email body
            body = {"Html": {"Data": html_content, "Charset": "UTF-8"}}
            if plain_content:
                body["Text"] = {"Data": plain_content, "Charset": "UTF-8"}
            
            # Prepare send parameters
            send_params = {
                "Source": sender,
                "Destination": {"ToAddresses": [to_email]},
                "Message": {
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": body
                }
            }
            
            # Add reply-to if provided
            if reply_to:
                send_params["ReplyToAddresses"] = [reply_to]
            
            # Add configuration set if configured
            if settings.AWS_SES_CONFIGURATION_SET:
                send_params["ConfigurationSetName"] = settings.AWS_SES_CONFIGURATION_SET
            
            # Add tags from metadata
            if metadata:
                send_params["Tags"] = [
                    {"Name": key, "Value": value}
                    for key, value in metadata.items()
                ]
            
            # Send email
            response = self.ses_client.send_email(**send_params)
            
            self.logger.info(
                "Email sent successfully via Amazon SES",
                extra={
                    "to_email": to_email,
                    "subject": subject,
                    "message_id": response["MessageId"]
                }
            )
            
            return {
                "success": True,
                "message_id": response["MessageId"],
                "provider": "ses",
                "to_email": to_email,
                "from_email": from_email,
                "sent_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Amazon SES error: {str(e)}")
            raise
    
    async def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str],
        from_email: str,
        from_name: str,
        reply_to: Optional[str],
        attachments: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Send email via SMTP (Mailpit for development)
        
        Mailpit provides a web interface at http://localhost:8025
        to view all sent emails during development
        """
        try:
            import aiosmtplib
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{from_name} <{from_email}>" if from_name else from_email
            message["To"] = to_email
            
            if reply_to:
                message["Reply-To"] = reply_to
            
            # Add plain text and HTML parts
            if plain_content:
                part1 = MIMEText(plain_content, "plain", "utf-8")
                message.attach(part1)
            
            part2 = MIMEText(html_content, "html", "utf-8")
            message.attach(part2)
            
            # Add attachments if provided
            if attachments:
                for attachment_data in attachments:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment_data.get("content"))
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {attachment_data.get('filename')}"
                    )
                    message.attach(part)
            
            # Send email via SMTP
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_TLS,
                start_tls=settings.SMTP_SSL
            )
            
            self.logger.info(
                "Email sent successfully via SMTP",
                extra={
                    "to_email": to_email,
                    "from_email": from_email,
                    "subject": subject,
                    "smtp_host": settings.SMTP_HOST
                }
            )
            
            return {
                "success": True,
                "message_id": f"smtp_{datetime.utcnow().timestamp()}",
                "provider": "smtp",
                "to_email": to_email,
                "from_email": from_email,
                "sent_at": datetime.utcnow().isoformat(),
                "note": "View email at http://localhost:8025 (Mailpit)"
            }
            
        except Exception as e:
            self.logger.error(f"SMTP error: {str(e)}")
            raise
    
    async def send_appointment_confirmation(
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
        Send appointment confirmation email
        
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
        from app.templates.email_templates import EmailTemplates
        
        subject = "Confirmation de rendez-vous - Santé"
        html_content = EmailTemplates.appointment_confirmation(
            patient_name=patient_name,
            doctor_name=doctor_name,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            appointment_type=appointment_type,
            cancellation_url=cancellation_url or "#"
        )
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            metadata={
                "template": "appointment_confirmation",
                "patient_name": patient_name
            }
        )
    
    async def send_appointment_reminder(
        self,
        to_email: str,
        patient_name: str,
        doctor_name: str,
        appointment_date: str,
        appointment_time: str
    ) -> Dict[str, Any]:
        """Send appointment reminder email"""
        from app.templates.email_templates import EmailTemplates
        
        subject = "Rappel de rendez-vous - Santé"
        html_content = EmailTemplates.appointment_reminder(
            patient_name=patient_name,
            doctor_name=doctor_name,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        )
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            metadata={
                "template": "appointment_reminder",
                "patient_name": patient_name
            }
        )
    
    async def send_password_reset(
        self,
        to_email: str,
        first_name: str,
        reset_url: str,
        expiry_minutes: int = 15
    ) -> Dict[str, Any]:
        """Send password reset email"""
        from app.templates.email_templates import EmailTemplates
        
        subject = "Réinitialisation de mot de passe - Santé"
        html_content = EmailTemplates.password_reset(
            first_name=first_name,
            reset_url=reset_url,
            expiry_minutes=expiry_minutes
        )
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            metadata={
                "template": "password_reset",
                "user_email": to_email
            }
        )
    
    async def send_prescription_ready(
        self,
        to_email: str,
        patient_name: str,
        medication_name: str,
        pickup_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send prescription ready notification"""
        from app.templates.email_templates import EmailTemplates
        
        subject = "Votre ordonnance est prête - Santé"
        html_content = EmailTemplates.prescription_ready(
            patient_name=patient_name,
            medication_name=medication_name,
            pickup_instructions=pickup_instructions or "Contactez votre pharmacie"
        )
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            metadata={
                "template": "prescription_ready",
                "patient_name": patient_name
            }
        )


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """
    Get singleton email service instance
    
    Returns:
        EmailService instance
    """
    global _email_service
    
    if _email_service is None:
        _email_service = EmailService()
    
    return _email_service
