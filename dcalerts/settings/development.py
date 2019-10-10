import os

from .base import *

# Basic settings
DEBUG = True
SECRET_KEY = '4+0!t6$#z^4y!ur2i^2*+&y5t@k84v_7d0(8=_pdz--6-5r%sa'
ALLOWED_HOSTS = ['*']

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True  
EMAIL_HOST = os.environ.get('TEST_EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('TEST_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('TEST_EMAIL_HOST_PASSWORD')
EMAIL_PORT = int(os.environ.get('TEST_EMAIL_PORT'))

# Settings for building URLs outside the app
EXTERNAL_URL_SCHEME = 'http'
EXTERNAL_URL_HOST = 'localhost:8000'
