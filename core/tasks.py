# tasks.py
from core.celery import celery_app
from django.core.mail import send_mail
from blog.models import Subscription
from core.settings import FROM_EMAIL

@celery_app.task(name='send_blog_notification')
def send_blog_notification(title):
    subscribers = Subscription.objects.all()
    subject = f'New Blog Uploaded: {title}'
    message = 'A new blog has been uploaded. Check it out now!'
    sender_email = FROM_EMAIL
    recipient_list = ['ankit@deepsense.in', ]
    send_mail(subject=subject, message=message, from_email=sender_email, recipient_list=recipient_list, fail_silently=False)
