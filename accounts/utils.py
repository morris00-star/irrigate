from sib_api_v3_sdk import ApiClient, Configuration, TransactionalEmailsApi
from sib_api_v3_sdk.models import SendSmtpEmail, SendSmtpEmailSender, SendSmtpEmailTo
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_brevo_transactional_email(to_email, subject, html_content):
    """
    Send email via Brevo API
    Returns True if successful, False otherwise
    """
    config = Configuration()
    config.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = TransactionalEmailsApi(ApiClient(config))

    sender = SendSmtpEmailSender(
        email=settings.DEFAULT_FROM_EMAIL,
        name="Smart Irrigation System"
    )
    to = [SendSmtpEmailTo(email=to_email)]

    email = SendSmtpEmail(
        sender=sender,
        to=to,
        subject=subject,
        html_content=html_content,
    )

    try:
        api_response = api_instance.send_transac_email(email)
        logger.info(f"Email sent to {to_email}. Message ID: {api_response.message_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False
