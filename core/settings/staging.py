"""
Staging settings for E-MEDATT project.
Used for pre-production testing and validation.
"""

from .base import *

# Debug should be off in staging, but can be enabled temporarily for troubleshooting
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"

# Allowed hosts - read from environment variable
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")

# CORS settings - specific origins only
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")

# Database - should be configured via environment variables
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.getenv("DB_NAME", "emedatt_staging"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# Cache configuration - Redis recommended for staging
CACHES = {
    "default": {
        "BACKEND": os.getenv(
            "CACHE_BACKEND", "django.core.cache.backends.redis.RedisCache"
        ),
        "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
    }
}

# Email backend - SMTP for staging
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Security settings - production-like but slightly relaxed
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True") == "True"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600  # 1 hour (less than production)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = False  # Not preloaded for staging
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Logging configuration - more verbose than production
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "staging.log"),
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 10,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "file"],
            "level": "DEBUG",  # More verbose for app code
            "propagate": False,
        },
    },
}

# Create logs directory if it doesn't exist
import os

logs_dir = os.path.join(BASE_DIR, "logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)
