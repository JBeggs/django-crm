"""
WSGI config for webcrm project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
from pathlib import Path

# Create required directories before Django loads
# This prevents errors when background threads start
BASE_DIR = Path(__file__).resolve().parent.parent
media_locks_dir = BASE_DIR / 'media' / 'locks'
staticfiles_dir = BASE_DIR / 'staticfiles'

# Create directories if they don't exist
media_locks_dir.mkdir(parents=True, exist_ok=True)
staticfiles_dir.mkdir(parents=True, exist_ok=True)

from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webcrm.settings')

application = get_wsgi_application()
