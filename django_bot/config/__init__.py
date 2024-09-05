# This ensures that the app is loaded when Django starts
# so that the @shared_task decorator will use it:

from .celery import app

__all__ = ('app',)