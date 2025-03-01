import uuid
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_email(data):
    email = EmailMessage(
        subject=data["subject"],
        body=data["body"],
        from_email=settings.EMAIL_HOST_USER,
        to=[data["to_email"]],
    )
    email.send()

def send_reset_password_email(email, full_name, reset_password_link):
    context_data = {
        "full_name": full_name,
        "reset_link": reset_password_link,
    }
    email_data = {
        "subject": (
            "Réinitialiser votre mot de passe"
        ),
        "to_email": [email],
        "text_content": render_to_string("emails/reset_password.txt", context_data),
        "html_content": render_to_string("emails/reset_password.html", context_data),
    }

    return send_email(email_data)

def generate_hex_id(length):
    return uuid.uuid4().hex[:length]
