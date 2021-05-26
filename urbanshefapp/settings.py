"""
Django settings for urbanshefapp project.

Generated by 'django-admin startproject' using Django 3.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from pathlib import Path
import environ
from django.contrib.messages import constants as messages
env = environ.Env()
# environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', True)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True



# Application definition
DJANGO_APP = [
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
THIRD_PARTY_APP = [
    'bootstrap5',
    'oauth2_provider',
    'social_django',
    'drf_social_oauth2',

    'drf_yasg',
    'multiselectfield',
    'rest_framework',
    'places',
    'crispy_forms',
    'tawkto'
]
LOCAL_APP = [
    'urbanshef',
]
INSTALLED_APPS = DJANGO_APP + THIRD_PARTY_APP + LOCAL_APP
CRISPY_TEMPLATE_PACK = 'bootstrap4'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'urbanshefapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR+'/urbanshef/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'urbanshefapp.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': env.str('DB_HOST', 'localhost'),
        'NAME': env.str('DB_NAME', 'urbanshef'),
        'USER': env.str('DB_USER', 'postgres'),
        'PASSWORD': env.str('DB_PASS', '12345'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# MEDIA_ROOT = '/vol/web/media'
# STATIC_ROOT = '/vol/web/static'

MEDIA_ROOT = 'mediafiles'
STATIC_ROOT = 'staticfiles'

# STATIC_ROOT = os.path.join(BASE_DIR, 'urbanshef/static')
# MEDIA_ROOT = os.path.join(BASE_DIR, 'urbanshef/static/media')

LOGIN_REDIRECT_URL = '/chef/'


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

AUTHENTICATION_BACKENDS = (
    'social_core.backends.facebook.FacebookOAuth2',
    'drf_social_oauth2.backends.DjangoOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Facebook configuration
SOCIAL_AUTH_FACEBOOK_KEY = env.str('SOCIAL_AUTH_FACEBOOK_KEY', '')
SOCIAL_AUTH_FACEBOOK_SECRET = env.str('SOCIAL_AUTH_FACEBOOK_SECRET', '')

# Define SOCIAL_AUTH_FACEBOOK_SCOPE to get extra permissions from Facebook.
# Email is not sent by default, to get it, you must request the email permission.
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id, name, email'
}

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'urbanshef.social_auth_pipeline.create_user_by_type',  # <--- set the path to the function
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)
STRIPE_PUBLISHABLE_KEY = env.str('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_CONNECT_CLIENT_ID = env.str('STRIPE_CONNECT_CLIENT_ID', '')
STRIPE_API_KEY = env.str('STRIPE_API_KEY', '')

# Sendgrid information
SENDGRID_API_KEY = env.str('SENDGRID_API_KEY', '')
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'  # this is exactly the value 'apikey'
EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
EMAIL_PORT = 587
EMAIL_USE_TLS = True
SENDGRID_SANDBOX_MODE_IN_DEBUG = False

DEFAULT_FROM_EMAIL = 'Urbanshef Team <no-reply@urbanshef.com>'

# Twilio account information to send notification of order to chefs
TWILIO_ACCOUNT_SID = env.str('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = env.str('TWILIO_AUTH_TOKEN', '')
TWILIO_NUMBER = env.str('TWILIO_NUMBER', '')

# Google map information
PLACES_MAPS_API_KEY = env.str('PLACES_MAPS_API_KEY', '')
PLACES_MAP_WIDGET_HEIGHT = 480
PLACES_MAP_OPTIONS = '{"center": { "lat": 38.971584, "lng": -95.235072 }, "zoom": 10}'
PLACES_MARKER_OPTIONS = '{"draggable": true}'

TAWKTO_ID_SITE = env.str('TAWKTO_ID_SITE', '')
TAWKTO_IS_SECURE = env.bool('TAWKTO_IS_SECURE', '')
TAWKTO_API_KEY = env.str('TAWKTO_API_KEY', '')


AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME", "")
AWS_STORAGE_REGION = env.str("AWS_STORAGE_REGION", "")


IS_AWS_S3 = (
    AWS_ACCESS_KEY_ID and
    AWS_SECRET_ACCESS_KEY and
    AWS_STORAGE_BUCKET_NAME and
    AWS_STORAGE_REGION
)

if IS_AWS_S3:
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    AWS_DEFAULT_ACL = env.str("AWS_DEFAULT_ACL", "public-read") #(optional; default is None which means the file will inherit the bucket’s permission)
    AWS_LOCATION = "media" # store files under directory `media/` in bucket `my-app-bucket`, If not set (optional: default is ‘’)
    DEFAULT_FILE_STORAGE = env.str(
        "DEFAULT_FILE_STORAGE", "storages.backends.s3boto3.S3Boto3Storage"
    )
MESSAGE_TAGS = {
    messages.INFO: 'alert alert-info',
    messages.WARNING: 'alert alert-warning',
    messages.ERROR: 'alert alert-danger',
}