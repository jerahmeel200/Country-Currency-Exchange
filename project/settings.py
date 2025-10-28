"""
Django settings for project deployed on Pxxl App.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv()

# -----------------------------------------------------
# SECURITY SETTINGS
# -----------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-secret-key")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ALLOWED_HOSTS should include Pxxl's domain or custom domain
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# -----------------------------------------------------
# APPLICATIONS
# -----------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "countries",
]

# -----------------------------------------------------
# MIDDLEWARE
# -----------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project.urls"

# -----------------------------------------------------
# TEMPLATES
# -----------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"

# -----------------------------------------------------
# DATABASE (MySQL)
# -----------------------------------------------------
# Pxxl provides MySQL credentials as environment variables
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME") or os.getenv("MYSQLDATABASE"),
        "USER": os.getenv("DB_USER") or os.getenv("MYSQLUSER"),
        "PASSWORD": os.getenv("DB_PASSWORD") or os.getenv("MYSQLPASSWORD"),
        "HOST": os.getenv("DB_HOST") or os.getenv("MYSQLHOST"),
        "PORT": os.getenv("DB_PORT") or os.getenv("MYSQLPORT", "3306"),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# -----------------------------------------------------
# CORS (Allow API access)
# -----------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL", "True").lower() == "true"

# -----------------------------------------------------
# PASSWORD VALIDATION
# -----------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------------------------------
# INTERNATIONALIZATION
# -----------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------
# STATIC & MEDIA FILES (Whitenoise for serving static files)
# -----------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -----------------------------------------------------
# REST FRAMEWORK (JSON-only)
# -----------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
}

# -----------------------------------------------------
# DEFAULT PRIMARY KEY FIELD TYPE
# -----------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------------------------------
# DEPLOYMENT RECOMMENDATIONS
# -----------------------------------------------------
# When using Pxxl App:
# - Add environment variables for DB credentials & SECRET_KEY in dashboard.
# - Set DEBUG=False and ALLOWED_HOSTS properly.
# - Run migrations and collectstatic after deploy.
#   Example (in Pxxl build command):
#   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
