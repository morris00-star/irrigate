import os
import sys
from pathlib import Path
import mimetypes
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables before any other settings
load_dotenv()

# Add MIME type for JavaScript files
mimetypes.add_type("application/javascript", ".js", True)


class CorrectMimeTypeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.endswith('.js'):
            response['Content-Type'] = 'application/javascript'
        return response


# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment Detection
IS_PRODUCTION = os.getenv('ENVIRONMENT') == 'production'
IS_DEVELOPMENT = not IS_PRODUCTION

# Security Settings
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if IS_DEVELOPMENT:
        SECRET_KEY = 'django-insecure-dev-key-only'  # For development only
    else:
        raise ValueError("SECRET_KEY must be set in production")

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true' if not IS_PRODUCTION else False

ALLOWED_HOSTS = [
    'irrigation-intelligent.onrender.com',
    'localhost',
    '127.0.0.1',
    '192.168.43.108',
    # Add other hosts as needed
]

# Application definition
INSTALLED_APPS = [
    # Third-party apps
    'channels',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_extensions',
    'cloudinary',
    'cloudinary_storage',

    # Local apps
    'accounts.apps.AccountsConfig',
    'irrigation',

    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'smart_irrigation.settings.CorrectMimeTypeMiddleware',
]

ROOT_URLCONF = 'smart_irrigation.urls'

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

# Database configuration
if IS_PRODUCTION:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST', 'd17i3fp5pdvs738dsju0 - a.frankfurt - postgres.render.com'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'OPTIONS': {
                'sslmode': 'require',
                'connect_timeout': 5  # Add connection timeout
            }
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'irrigation', 'static'),
    os.path.join(BASE_DIR, 'accounts', 'static'),
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Cloudinary
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
    'SECURE': True,
    'MEDIA_TAG': 'profile_pics',
    'INVALIDATE': True,
}

# Authentication
AUTH_USER_MODEL = 'accounts.CustomUser'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

# Email Configuration
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
BREVO_API_KEY = os.getenv('BREVO_API_KEY')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

# Site information for password reset emails
SITE_ID = 1

SITE_NAME = "Irrigation Intelligent"

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'irrigation.authentication.APIKeyAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '720/hour',
        'user': '1000/day'
    },
}

# Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(os.getenv('REDIS_HOST', '127.0.0.1'), int(os.getenv('REDIS_PORT', 6379)))],
        },
    },
}

# Security Settings
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://192.168.43.108:8000",
]
CORS_ORIGIN_ALLOW_ALL = DEBUG  # Only allow all in development

# Custom irrigation settings
IRRIGATION_SYSTEM = {
    'DEFAULT_SOIL_MOISTURE_THRESHOLD': 50,
    'DEFAULT_WATERING_DURATION': 10,
    'MAX_SENSOR_DATA_AGE': 3600,
    'SENSOR_DATA_INTERVAL': 300,
}

EGOSMS_CONFIG = {
    'USERNAME': os.getenv('EGOSMS_USERNAME'),
    'PASSWORD': os.getenv('EGOSMS_PASSWORD'),
    'SENDER_ID': os.getenv('EGOSMS_SENDER_ID', 'IRRIGATE'),
    'API_URL': os.getenv('EGOSMS_API_URL', 'https://www.egosms.co/api/v1/plain/'),
    'TIMEOUT': 10,  # seconds
    'PRIORITY': 0,  # 0=normal, 1=high
    'TEST_MODE': os.getenv('EGOSMS_TEST_MODE', 'False').lower() == 'true',
}

CRON_SECRET_KEY = os.getenv('CRON_SECRET_KEY', 'dev-secret-key-change-me')

DEFAULT_CHARSET = 'utf-8'

# Celery
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_TIMEZONE = 'Africa/Nairobi'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG' if DEBUG else 'INFO',
    },
}

# Ensure directories exist
os.makedirs(os.path.join(MEDIA_ROOT, 'profile_pics'), exist_ok=True)
os.makedirs(STATIC_ROOT, exist_ok=True)
