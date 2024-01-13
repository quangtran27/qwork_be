'''
Django settings for qwork_be project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
'''

import json
import os
from datetime import timedelta
from pathlib import Path

import environ
import firebase_admin
from firebase_admin import credentials

env = environ.Env(DEBUG=(bool, False))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('ALLOWED_HOSTS').split(' ')

# Application definition
INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',

	# apps
	'addresses',
	'applications',
	'authentication',
	'candidates',
	'jobs',
  'recruiters',
	'users',

	# libs
	'corsheaders',
	'rest_framework',
	'rest_framework_simplejwt',
	'rest_framework_swagger',
  'drf_yasg',
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
  'whitenoise.middleware.WhiteNoiseMiddleware',
	'corsheaders.middleware.CorsMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'djangorestframework_camel_case.middleware.CamelCaseMiddleWare',
]

CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS').split(' ')

CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
  'DEFAULT_AUTHENTICATION_CLASSES': (
    # 'rest_framework_simplejwt.authentication.JWTAuthentication',
  ),
	'DEFAULT_RENDERER_CLASSES': (
		'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
		'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
	),
	'DEFAULT_PARSER_CLASSES': (
		'djangorestframework_camel_case.parser.CamelCaseFormParser',
		'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
		'djangorestframework_camel_case.parser.CamelCaseJSONParser',
	),
  'DEFAULT_PAGINATION_CLASS': 'utils.pagination.CustomPageNumberPagination',
  'PAGE_SIZE': 9
}

SIMPLE_JWT = {
	'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
	'REFRESH_TOKEN_LIFETIME': timedelta(days=90),
	'ROTATE_REFRESH_TOKENS': True,
	'BLACKLIST_AFTER_ROTATION': True,
	'UPDATE_LAST_LOGIN': False,

	'ALGORITHM': 'HS256',
	'SIGNING_KEY': SECRET_KEY,
	'VERIFYING_KEY': '',
	'AUDIENCE': None,
	'ISSUER': None,
	'JSON_ENCODER': None,
	'JWK_URL': None,
	'LEEWAY': 0,

	'AUTH_HEADER_TYPES': ('Bearer',),
	'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
	'USER_ID_FIELD': 'id',
	'USER_ID_CLAIM': 'user_id',
	'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

	'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
	'TOKEN_TYPE_CLAIM': 'token_type',
	'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

	'JTI_CLAIM': 'jti',

	'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
	'SLIDING_TOKEN_LIFETIME': timedelta(minutes=15),
	'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=90),

	'TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer',
	'TOKEN_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSerializer',
	'TOKEN_VERIFY_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenVerifySerializer',
	'TOKEN_BLACKLIST_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenBlacklistSerializer',
	'SLIDING_TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer',
	'SLIDING_TOKEN_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer',

	# Store refresh token in HTTP-only cookie
	'AUTH_COOKIE': 'refresh_token',
	'AUTH_COOKIE_DOMAIN': None,     # A string like "example.com", or None for standard domain cookie.
	'AUTH_COOKIE_SECURE': True,    # Whether the auth cookies should be secure (https:// only).
	'AUTH_COOKIE_HTTP_ONLY' : False, # Http only cookie flag.It's not fetch by javascript.
	'AUTH_COOKIE_PATH': '/',        # The path of the auth cookie.
	'AUTH_COOKIE_SAMESITE': 'None',  # Whether to set the flag restricting cookie leaks on cross-site requests.
}

ROOT_URLCONF = 'qwork_be.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [],
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

WSGI_APPLICATION = 'qwork_be.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': env('DATABASE_NAME'),
    'USER': env('DATABASE_USERNAME'),
    'PASSWORD': env('DATABASE_PASSWORD'),
    'HOST': env('DATABASE_HOST'),
    'PORT': env('DATABASE_PORT'),
  }
}

# Auth configs
AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = [
  'users.backends.EmailBackend'
]

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_TZ = False
USE_I18N = True
TIME_ZONE = 'Asia/Bangkok'



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Firebase
cred = credentials.Certificate('./credentials.json')
firebase_admin.initialize_app(cred, {'storageBucket': 'qwork-aa383.appspot.com'})

DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
FIREBASE_CREDENTIALS = json.loads(open('./credentials.json').read())

# Email config
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
