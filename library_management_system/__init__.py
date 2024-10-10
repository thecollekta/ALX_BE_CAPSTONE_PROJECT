# library_management_system/__init__.py

# Import Celery
from .celery import app as celery_app

__all__ = ("celery_app",)