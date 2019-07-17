import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'mvazb9#yw1*vro%mbz-dm*72i-=a0l$ppgvqi)lyaq2x&*03z9'

DEBUG = True

ALLOWED_HOSTS = ["printmycopy.com", "www.printmycopy.com", "209.124.64.50", "*"]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'accounts',
    'portal',
    'transactions',
    'stations',
    'wallets',
    'recharges',
    'payments',
    'dealers',
    'rates',
    'complaints',

    'crispy_forms',
    'paywix',

    'simple_history',
    'widget_tweaks',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'ewayprint.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ewayprint.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': '',
#         'USER': '',
#         'PASSWORD': '*',
#         'HOST': '',
#         'PORT': '',
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = False


STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, "static/")
# STATIC_ROOT = "/var/www/static-root/"

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, "media/")
# MEDIA_ROOT = "/var/www/media-root/"


from django.contrib import messages
from django.urls import reverse_lazy

MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}


API_KEY_2FA = "c9ef2a2e-806a-11e9-ade6-0200cd936042"

AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',

)

CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGIN_URL = reverse_lazy('accounts:login')
LOGIN_REDIRECT_URL = reverse_lazy('portal:home')
#
# SITE_DOMAIN = "http://www.printmycopy.com/"
# SITE_DOMAIN_NAKED = "http://www.printmycopy.com"


SITE_DOMAIN = "http://127.0.0.1:8000/"
SITE_DOMAIN_NAKED = "http://127.0.0.1:8000"

# SITE_DOMAIN = "http://192.168.0.111:8080/"
# SITE_DOMAIN_NAKED = "http://192.168.0.111:8080"

# Payments App
PAYU_MERCHANT_KEY = "mdLYzH6I"
PAYU_KEY = "mdLYzH6I"
PAYU_SALT = "BgIZKB6m9D"
PAYMENT_MODE ='TEST'
#
PAYU_SUCCESS_URL = SITE_DOMAIN + "payments/success/"
PAYU_FAILURE_URL = SITE_DOMAIN + "payments/failure/"

#
# PAYU_SUCCESS_URL = "payments:payment_success"
# PAYU_FAILURE_URL = "payments:payment_failure"
