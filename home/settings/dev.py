'''Use this for development'''

from .base import *

ALLOWED_HOSTS += ['127.0.0.1']
DEBUG = True

WSGI_APPLICATION = 'home.wsgi.dev.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CORS_ORIGIN_WHITELIST = (
    'http://localhost:3000',
)

# Ajout de la configuration pour CORS - MA
CORS_ALLOW_CREDENTIALS = True

# Stripe

STRIPE_PUBLIC_KEY = config('STRIPE_TEST_PUBLIC_KEY')
STRIPE_SECRET_KEY = config('STRIPE_TEST_SECRET_KEY')
