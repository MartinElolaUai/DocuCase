import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.models import GroupSubscription, User, NotificationLog


def get_email_template(notification_type: str, data: Dict[str, Any]) -> Dict[str, str]:
    """Generate email subject and HTML body based on notification type."""
    
    if notification_type == "request_new":
        request = data.get("request", {})
        application = data.get("application", {})
        requester = data.get("requester", {})
        
        return {
            "subject": f"[DashCase] Nueva solicitud de caso de prueba: {request.get('title', '')}",
            "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #1a365d;">Nueva Solicitud de Caso de Prueba</h2>
                    <p><strong>Título:</strong> {request.get('title', '')}</p>
                    <p><strong>Aplicación:</strong> {application.get('name', '')}</p>
                    <p><strong>Solicitante:</strong> {requester.get('first_name', '')} {requester.get('last_name', '')}</p>
                    <p><strong>Descripción:</strong></p>
                    <p style="background: #f7fafc; padding: 15px; border-radius: 5px;">
                        {request.get('description', '')}
                    </p>
                    <p style="margin-top: 20px;">
                        <a href="{settings.FRONTEND_URL}/requests/{request.get('id', '')}" 
                           style="background: #3182ce; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                            Ver Solicitud
                        </a>
                    </p>
                </div>
            """
        }
    
    elif notification_type == "request_status_change":
        request = data.get("request", {})
        previous_status = data.get("previousStatus", "")
        new_status = data.get("newStatus", "")
        
        status_labels = {
            "NEW": "Nueva",
            "IN_ANALYSIS": "En Análisis",
            "APPROVED": "Aprobada",
            "REJECTED": "Rechazada",
            "IMPLEMENTED": "Implementada",
        }
        
        return {
            "subject": f"[DashCase] Cambio de estado en solicitud: {request.get('title', '')}",
            "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #1a365d;">Actualización de Solicitud</h2>
                    <p><strong>Título:</strong> {request.get('title', '')}</p>
                    <p><strong>Estado anterior:</strong> {status_labels.get(previous_status, previous_status)}</p>
                    <p><strong>Nuevo estado:</strong> {status_labels.get(new_status, new_status)}</p>
                    <p style="margin-top: 20px;">
                        <a href="{settings.FRONTEND_URL}/requests/{request.get('id', '')}" 
                           style="background: #3182ce; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                            Ver Solicitud
                        </a>
                    </p>
                </div>
            """
        }
    
    elif notification_type == "pipeline_failed":
        pipeline = data.get("pipeline", {})
        failed_count = data.get("failedCount", 0)
        web_url = pipeline.get("web_url", "")
        
        button_html = ""
        if web_url:
            button_html = f"""
                <p style="margin-top: 20px;">
                    <a href="{web_url}" 
                       style="background: #c53030; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        Ver Pipeline en GitLab
                    </a>
                </p>
            """
        
        return {
            "subject": f"[DashCase] ⚠️ Pipeline fallido en {pipeline.get('branch', '')}",
            "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #c53030;">Pipeline Fallido</h2>
                    <p><strong>Branch:</strong> {pipeline.get('branch', '')}</p>
                    <p><strong>Pipeline ID:</strong> {pipeline.get('gitlab_pipeline_id', '')}</p>
                    <p><strong>Casos fallidos:</strong> {failed_count}</p>
                    {button_html}
                </div>
            """
        }
    
    else:
        return {
            "subject": "[DashCase] Notificación",
            "html": f"<p>{str(data)}</p>"
        }


async def send_email(recipients: List[str], subject: str, html_body: str) -> bool:
    """Send an email using SMTP."""
    if not settings.SMTP_USER or not settings.SMTP_PASS:
        print(f"SMTP not configured, skipping email to: {recipients}")
        print(f"Subject: {subject}")
        return False
    
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.SMTP_FROM
        message["To"] = ", ".join(recipients)
        
        html_part = MIMEText(html_body, "html")
        message.attach(html_part)
        
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASS,
            start_tls=True,
        )
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


async def send_notification(
    db: Session,
    notification_type: str,
    group_id: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None
) -> None:
    """Send notification to relevant users."""
    data = data or {}
    recipients: List[str] = []
    
    # Get subscribers for the group
    if group_id:
        subscriptions = db.query(GroupSubscription).filter(
            GroupSubscription.group_id == group_id
        ).all()
        
        for sub in subscriptions:
            user = db.query(User).filter(User.id == sub.user_id).first()
            if user and user.status.value == "ACTIVE":
                recipients.append(user.email)
        
        # Include admins for important notifications
        if notification_type in ["request_new", "pipeline_failed"]:
            admins = db.query(User).filter(
                User.role == "ADMIN",
                User.status == "ACTIVE"
            ).all()
            for admin in admins:
                if admin.email not in recipients:
                    recipients.append(admin.email)
    
    # Add requester for status change notifications
    if notification_type == "request_status_change":
        request = data.get("request", {})
        requester = request.get("requester", {})
        requester_email = requester.get("email")
        if requester_email and requester_email not in recipients:
            recipients.append(requester_email)
    
    if not recipients:
        print(f"No recipients for notification: {notification_type}")
        return
    
    template = get_email_template(notification_type, data)
    subject = template["subject"]
    html_body = template["html"]
    
    # Check if SMTP is configured
    if not settings.SMTP_USER or not settings.SMTP_PASS:
        print("SMTP not configured, skipping email notification")
        print(f"Would send to: {recipients}")
        print(f"Subject: {subject}")
        
        # Log the notification anyway
        log = NotificationLog(
            type=notification_type,
            recipients=recipients,
            subject=subject,
            body=html_body,
            status="skipped",
            extra_metadata=data
        )
        db.add(log)
        db.commit()
        return
    
    # Send email
    success = await send_email(recipients, subject, html_body)
    
    # Log notification
    log = NotificationLog(
        type=notification_type,
        recipients=recipients,
        subject=subject,
        body=html_body,
        status="sent" if success else "failed",
        error=None if success else "Email send failed",
        extra_metadata=data
    )
    db.add(log)
    db.commit()
    
    if success:
        print(f"Notification sent: {notification_type} to {len(recipients)} recipients")

