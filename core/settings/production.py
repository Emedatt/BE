"""
Production settings for E-MEDATT project.
All sensitive values must be provided via environment variables.
"""

from .base import *

# SECURITY WARNING: Debug must NEVER be True in production
DEBUG = False

# Allowed hosts - must be explicitly set via environment variable
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")
if not ALLOWED_HOSTS or ALLOWED_HOSTS == [""]:
    raise ValueError(
        "DJANGO_ALLOWED_HOSTS environment variable must be set in production"
    )

# CORS settings - specific origins only
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
if not CORS_ALLOWED_ORIGINS or CORS_ALLOWED_ORIGINS == [""]:
    raise ValueError(
        "CORS_ALLOWED_ORIGINS environment variable must be set in production"
    )

# Database - must be configured via environment variables
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": 600,  # Connection pooling
        "OPTIONS": {
            "sslmode": os.getenv("DB_SSLMODE", "require"),
        },
    }
}

# Validate database configuration
required_db_vars = ["DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST"]
for var in required_db_vars:
    if not os.getenv(var):
        raise ValueError(f"{var} environment variable must be set in production")

# Cache configuration - Redis required for production
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
            },
        },
    }
}

if not os.getenv("REDIS_URL"):
    raise ValueError("REDIS_URL environment variable must be set in production")

# Email backend - SMTP required for production
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Validate email configuration
required_email_vars = ["EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD", "DEFAULT_FROM_EMAIL"]
for var in required_email_vars:
    if not os.getenv(var):
        raise ValueError(f"{var} environment variable must be set in production")

# Security settings - maximum security for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Session settings
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"
SESSION_COOKIE_AGE = 3600  # 1 hour

# CSRF settings
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Strict"
CSRF_USE_SESSIONS = True

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files (if used)
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# Admin URL - can be customized via environment variable for security
ADMIN_URL = os.getenv("ADMIN_URL", "admin/")

# Logging configuration - production optimized
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
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
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "production.log"),
            "maxBytes": 1024 * 1024 * 50,  # 50 MB
            "backupCount": 20,
            "formatter": "verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "error.log"),
            "maxBytes": 1024 * 1024 * 50,  # 50 MB
            "backupCount": 20,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "error_file"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console", "error_file"],
            "level": "ERROR",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Create logs directory if it doesn't exist
import os

logs_dir = os.path.join(BASE_DIR, "logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Additional security headers
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

# Rate limiting (if using throttling)
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = [
    "rest_framework.throttling.AnonRateThrottle",
    "rest_framework.throttling.UserRateThrottle",
]
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
    "anon": os.getenv("THROTTLE_RATE_ANON", "100/hour"),
    "user": os.getenv("THROTTLE_RATE_USER", "1000/hour"),
}
