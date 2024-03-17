import os
from celery import Celery


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Create a Celery instance
celery_app = Celery('core')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.conf.broker_connection_retry_on_startup = True

# Load task modules from all registered Django app configs.
celery_app.autodiscover_tasks()

@celery_app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
