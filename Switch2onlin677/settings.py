from pathlib import Path
from datetime import timedelta
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_yasg",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "debug_toolbar",
    "api",
    "accounts",
    "agent_manage",
    "conversation",
    "django_filters",
    "leads",
    "dashboard",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "accounts.middleware.ActiveUserMiddleware",
]

ROOT_URLCONF = "Switch2onlin677.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "Switch2onlin677.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

AUTH_USER_MODEL = "accounts.User"
INTERNAL_IPS = [
    "127.0.0.1",
]
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
# STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://charissa-intuitable-corroboratorily.ngrok-free.dev",
    "https://switch2onlin677-frontend.vercel.app",
]
ALLOWED_HOSTS = [
    h.strip() for h in config("ALLOWED_HOSTS", default="127.0.0.1").split(",")
]
# ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1").split(",")
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in config("CSRF_TRUSTED_ORIGINS", default="").split(",") if o
]
# CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="").split(",")
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Add ngrok-skip-browser-warning to allowed headers
from corsheaders.defaults import default_headers

CORS_ALLOW_HEADERS = list(default_headers) + [
    "ngrok-skip-browser-warning",
]

# Tell Django we are behind a proxy that provides HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
proxy_ssl_header = config("SECURE_PROXY_SSL_HEADER", default=None)
if proxy_ssl_header:
    # If set in .env as "HTTP_X_FORWARDED_PROTO,https"
    SECURE_PROXY_SSL_HEADER = tuple(proxy_ssl_header.split(","))

EMAIL_BACKEND = config("EMAIL_BACKEND")
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT")
EMAIL_USE_TLS = config("EMAIL_USE_TLS")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")

# Meta API Configuration
META_VERIFY_TOKEN = config("META_VERIFY_TOKEN", default="my_verify_token")

# Facebook Page Access Token (for Messenger)
META_FB_PAGE_ACCESS_TOKEN = config("META_FB_PAGE_ACCESS_TOKEN", default="")

# Instagram Page Access Token (starts with 'IGA...', for Instagram Messaging)
META_IG_PAGE_ACCESS_TOKEN = config("META_IG_PAGE_ACCESS_TOKEN", default="")

# WhatsApp Cloud API
META_WHATSAPP_PHONE_NUMBER_ID = config("META_WHATSAPP_PHONE_NUMBER_ID", default="")
META_WHATSAPP_BUSINESS_ACCOUNT_ID = config(
    "META_WHATSAPP_BUSINESS_ACCOUNT_ID", default=""
)

META_PAGE_ACCESS_TOKEN = config("META_PAGE_ACCESS_TOKEN", default="")
META_PAGE_ID = config("META_PAGE_ID", default="")
META_INSTAGRAM_BUSINESS_ACCOUNT_ID = config(
    "META_INSTAGRAM_BUSINESS_ACCOUNT_ID", default=""
)

AI_BOT_BASE_URL = config("AI_BOT_BASE_URL", default="")
LEADS_API_KEY = config("LEADS_API_KEY", default="")
