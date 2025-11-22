# Multi-Environment Settings Configuration

This project uses a modular settings structure to manage different configurations for development, staging, and production environments.

## Structure

```
core/
└── settings/
    ├── __init__.py       # Auto-loads the correct environment
    ├── base.py           # Common settings shared across all environments
    ├── development.py    # Local development settings
    ├── staging.py        # Staging environment settings
    └── production.py     # Production environment settings
```

## Usage

### Setting the Environment

The settings are automatically loaded based on the `DJANGO_ENVIRONMENT` environment variable:

```bash
# Development (default if not set)
export DJANGO_ENVIRONMENT=development

# Staging
export DJANGO_ENVIRONMENT=staging

# Production
export DJANGO_ENVIRONMENT=production
```

### Environment-Specific Configurations

#### Development
- `DEBUG = True`
- Permissive CORS (allows all origins)
- SQLite database
- Console email backend (prints emails to console)
- Relaxed security settings

#### Staging
- `DEBUG` configurable via `DJANGO_DEBUG` env var (default: False)
- Specific CORS origins (via `CORS_ALLOWED_ORIGINS`)
- PostgreSQL database (configurable via env vars)
- Redis cache
- SMTP email backend
- Production-like security with verbose logging

#### Production
- `DEBUG = False` (enforced)
- Strict CORS configuration (required)
- PostgreSQL database with SSL (required)
- Redis cache (required)
- SMTP email backend (required)
- Maximum security settings
- Minimal logging (warnings and errors only)

## Required Environment Variables

### Development
No required environment variables (uses sensible defaults).

### Staging
```bash
DJANGO_ALLOWED_HOSTS=staging.example.com
CORS_ALLOWED_ORIGINS=https://staging.example.com,https://staging-admin.example.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=emedatt_staging
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
REDIS_URL=redis://localhost:6379/1
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
DEFAULT_FROM_EMAIL=noreply@example.com
```

### Production
All staging variables plus:
```bash
DJANGO_SECRET_KEY=your-secure-secret-key-here
REDIS_URL=redis://production-redis:6379/0
# Database SSL mode
DB_SSLMODE=require
# Optional: Custom admin URL for security
ADMIN_URL=custom-admin-path/
# Optional: Rate limiting
THROTTLE_RATE_ANON=100/hour
THROTTLE_RATE_USER=1000/hour
```

## Security Considerations

### Production Settings
The production settings enforce:
- SSL redirect
- Secure cookies (HTTPS only)
- HSTS headers
- XSS protection
- Content type sniffing prevention
- Clickjacking protection
- CSRF protection

### Secret Management
Never commit sensitive values to version control. Use:
- Environment variables
- Secret management services (AWS Secrets Manager, Azure Key Vault, etc.)
- `.env` files (added to `.gitignore`)

## Running Commands

### With Environment Variable
```bash
DJANGO_ENVIRONMENT=production python manage.py check
```

### With Default (Development)
```bash
python manage.py runserver
```

## Testing Different Environments Locally

```bash
# Test development settings
python manage.py check

# Test staging settings
DJANGO_ENVIRONMENT=staging python manage.py check --deploy

# Test production settings (will fail without required env vars)
DJANGO_ENVIRONMENT=production python manage.py check --deploy
```

## Deployment

### Docker
```dockerfile
ENV DJANGO_ENVIRONMENT=production
```

### systemd
```ini
[Service]
Environment="DJANGO_ENVIRONMENT=production"
```

### Kubernetes
```yaml
env:
  - name: DJANGO_ENVIRONMENT
    value: "production"
```

## Logging

### Development
- Console output
- INFO level for general messages
- Verbose formatting

### Staging
- Console and file output
- Detailed logging for debugging
- Separate error log file
- 10 MB log file rotation

### Production
- Console and file output
- WARNING level for general messages
- ERROR level for critical issues
- 50 MB log file rotation
- 20 backup files

## Troubleshooting

### Import Errors
If you encounter model import errors, ensure you're using:
- `settings.AUTH_USER_MODEL` for ForeignKey references
- `from django.conf import settings` for accessing settings

### Missing Environment Variables
Production settings will raise `ValueError` if required environment variables are missing. Check the error message for which variable is required.

### Database Connection Issues
Verify:
- Database credentials are correct
- Database server is accessible
- SSL mode matches your database configuration

## Migration Notes

When switching from the old single `settings.py` to this structure:
1. The old file is backed up as `settings.py.bak`
2. All imports of `core.settings` still work (points to `core/settings/__init__.py`)
3. No code changes needed in other files
4. Set `DJANGO_ENVIRONMENT` before running migrations in production

## Additional Resources

- [Django Settings Best Practices](https://docs.djangoproject.com/en/stable/topics/settings/)
- [12-Factor App Configuration](https://12factor.net/config)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
