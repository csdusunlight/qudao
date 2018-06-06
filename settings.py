"""
Django settings for mobile project.

Generated by 'django-admin startproject' using Django 1.8.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '==4cwx_97e&h+7*r57*=*s&g&j*c4uy3l!jw)k!gvbpbxo$z!^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1',]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djcelery',
    'account',
    'wafuli',
    'DjangoUeditor',
    'captcha',
    'wafuli_admin',
    'rest_framework',
    'django_filters',
    'homepage',
    'statistic',
    'coupon',
    'docs',
    'mobi',
    'weixin',
    'merchant',
    'xiaochengxu',
)

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5,
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
#     'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
}

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'mobi.middleware.MobileDetectionMiddleware',
)

ROOT_URLCONF = 'dragon.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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


STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

WSGI_APPLICATION = 'dragon.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {
    'default': {
#         'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/0/',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'test',
#         'USER': 'root',
#         'PASSWORD': 'Xianjian7',
#     }
# }


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), '..', 'media').replace('\\','/')
# STATIC_ROOT = os.path.join(os.path.dirname(__file__), '..', 'static').replace('\\','/')
STATIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'static').replace('\\','/')
MEDIA_URL = '/media/'
AUTH_USER_MODEL = 'account.MyUser'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'account_index'

CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
#CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge'
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_dots',)

SESSION_EXPIRE_AT_BROWSER_CLOSE = False


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
                    'format': '[%(levelname)s][%(asctime)s][%(module)s][thread-%(process)d-%(thread)d]%(message)s'
        },
        'simple': {
                   'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
                'default':{
                    'level':'DEBUG',
                    'class':'logging.handlers.RotatingFileHandler',
                    'filename': os.path.join(BASE_DIR, 'debug.log'),
                    'maxBytes': 1024*1024*100,
                    'backupCount': 5,
                    'formatter':'verbose',
                },
                'file': {
                    'level': 'DEBUG',
                    'class': 'logging.FileHandler',
                    'filename': os.path.join(BASE_DIR, 'debug.log'),
                    'formatter': 'verbose',
                },
    },
    'loggers': {
        'django': {
            'handlers': ['default',],
            'level': 'DEBUG',
            'propagate': False
        },
        'wafuli': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
DOMAIN_URL = "http://127.0.0.1:8000"
AWARD_RATE = 0.01
AWARD_SCORES = 100
APPID = 'wxdb5c8596f7e1ce3f'
SECRET = '7b7282ca4e4dd977d6ff15c0d1aa5559'
NONCESTR = 'AXMPT2016sncfeuiw'
FULIUNION_DOMAIN = 'test.fuliunion.com'
FANSHU_DOMAIN = '127.0.0.1:8000'


import djcelery
djcelery.setup_loader()

BROKER_URL = 'amqp://guest:guest@localhost:5672//'
BROKER_CONNECTION_TIMEOUT = 0.1

REDIS_TIMEOUT=7*24*60*60
CUBES_REDIS_TIMEOUT=60*60
NEVER_REDIS_TIMEOUT=365*24*60*60
SECURE_BROWSER_XSS_FILTER = True