# library_management_system/accounts/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task(bind=True, max_retries=3)
def send_email_async(subject, message, recipient_list):
    """
    Asynchronous task to send an email.
    Celery workers invoke this task and send an email in the background.
    """
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipient_list,
        fail_silently=False, # Set to ensure failed emails do not affect others.
    )