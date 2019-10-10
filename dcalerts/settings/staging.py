import os

from .base import *

# Overall settings
APP_PORT = os.environ.get('APP_PORT') or 8000
DEBUG = False
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
ALLOWED_HOSTS = [os.environ.get('SITENAME') or f'localhost:{APP_PORT}']
PRODUCTION = True

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True  
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT'))

# Settings for building URLs outside the app
EXTERNAL_URL_SCHEME = os.environ.get)'EXTERNAL_URL_SCHEME') or 'http'
EXTERNAL_URL_HOST = os.environ.get('SITENAME') or f'localhost:{APP_PORT}'

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
