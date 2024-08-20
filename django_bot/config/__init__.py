# This ensures that the app is loaded when Django starts
# so that the @shared_task decorator will use it:

from .celery import app as celery_app

__all__ = ('celery_app',)