# library_management_system/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Default Django settings module for 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management_system.settings')

# Celery object instantiation
app = Celery('library_management_system')

# Celery Timezone settings
app.conf.enable_utc = False
app.conf.update(timezone = 'Africa/Accra')

# Load Celery configuration from Django's settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery Beat settings
app.conf.beat_schedule = {
    'check-overdue-books-every-day at 6am': {
        'task': 'transactions.tasks.check_overdue_books',
        'schedule': crontab(hour=6, minute=0),  # Runs daily at midnight
    },
}

# Automatically discover tasks from installed app
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')