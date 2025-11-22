# Getting Started - E-MEDATT Backend

This guide will help you set up the E-MEDATT backend for local development.

## Prerequisites

- Python 3.12+ 
- pip (Python package manager)
- Git
- PostgreSQL (optional for staging/production testing)
- Redis (optional for staging/production testing)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Emedatt/BE.git
cd BE
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your preferred editor
nano .env  # or vim, code, etc.
```

**Minimum required for development:**
```env
DJANGO_ENVIRONMENT=development
DJANGO_SECRET_KEY=genrate-and-add-your-secret-key-here
```

### 5. Run Migrations

```bash
# Note: There may be migration issues in the current codebase
# This is a known issue being addressed
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

The API will be available at: `http://127.0.0.1:8000/`

## Environment Configuration

This project uses a **multi-environment settings structure** for managing different configurations.

### Environment Selection

Set the `DJANGO_ENVIRONMENT` variable to control which settings are loaded:

```bash
# Development (default - uses SQLite, DEBUG=True, permissive CORS)
export DJANGO_ENVIRONMENT=development
python manage.py runserver

# Staging (uses PostgreSQL, DEBUG configurable, production-like security)
export DJANGO_ENVIRONMENT=staging
python manage.py runserver

# Production (strict security, requires all env vars)
export DJANGO_ENVIRONMENT=production
python manage.py runserver
```

### Settings Structure

```
core/settings/
├── __init__.py       # Auto-loads correct environment
├── base.py           # Shared settings across all environments
├── development.py    # Local development (DEBUG=True, SQLite)
├── staging.py        # Pre-production testing (PostgreSQL, Redis)
└── production.py     # Production deployment (strict security)
```

For detailed configuration, see **[SETTINGS_CONFIGURATION.md](SETTINGS_CONFIGURATION.md)**

## Development Workflow

### Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test apps.accounts

# Run with coverage (if installed)
coverage run --source='.' manage.py test
coverage report
```

### API Documentation

Once the server is running, access the API documentation:

- **Swagger UI**: http://127.0.0.1:8000/swagger/
- **ReDoc**: http://127.0.0.1:8000/redoc/
- **OpenAPI Schema**: http://127.0.0.1:8000/api/schema/

### Django Admin

Access the admin interface at: http://127.0.0.1:8000/admin/

Use the superuser credentials you created earlier.

## Project Structure

```
BE/
├── apps/                      # Django applications
│   ├── accounts/              # User authentication & profiles
│   ├── appointments/          # Appointment management
│   ├── billing/               # Payment processing
│   ├── healthrecords/         # Medical records
│   ├── labs/                  # Lab test management
│   ├── notification/          # Notifications system
│   ├── prescriptions/         # Prescription management
│   ├── rating/                # Rating system
│   ├── telehealth/            # Video consultation
│   └── ...
├── core/                      # Project configuration
│   ├── settings/              # Environment-specific settings
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── staging.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── documentation/             # Documentation
├── utils/                     # Utility scripts
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── .env.example               # Example environment variables
└── README.md                  # Project overview
```

## Common Commands

### Database Management

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations status
python manage.py showmigrations

# Reset database (SQLite - development only)
rm db.sqlite3
python manage.py migrate
```

### Django Shell

```bash
# Interactive Python shell with Django context
python manage.py shell

# Example: Create a user programmatically
python manage.py shell
>>> from apps.accounts.models import User
>>> user = User.objects.create_user(
...     email='test@example.com',
...     password='securepass123',
...     first_name='John',
...     last_name='Doe',
...     role='patient'
... )
```

### Collect Static Files

```bash
# For production deployment
python manage.py collectstatic --noinput
```

### System Check

```bash
# Check for common Django issues
python manage.py check

# Check deployment configuration
python manage.py check --deploy
```

## Environment Variables Reference

### Essential Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DJANGO_ENVIRONMENT` | Environment selection (development/staging/production) | development | No |
| `DJANGO_SECRET_KEY` | Django secret key | - | Yes (production) |
| `DJANGO_DEBUG` | Debug mode | True (dev), False (staging/prod) | No |

### Database Variables (Staging/Production)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DB_ENGINE` | Database engine | django.db.backends.postgresql | No |
| `DB_NAME` | Database name | - | Yes (staging/prod) |
| `DB_USER` | Database user | - | Yes (staging/prod) |
| `DB_PASSWORD` | Database password | - | Yes (staging/prod) |
| `DB_HOST` | Database host | localhost | Yes (staging/prod) |
| `DB_PORT` | Database port | 5432 | No |
| `DB_SSLMODE` | SSL mode | require | No |

### Security Variables (Staging/Production)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts | - | Yes (staging/prod) |
| `CORS_ALLOWED_ORIGINS` | Comma-separated CORS origins | - | Yes (staging/prod) |

### Email Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `EMAIL_HOST` | SMTP host | smtp.gmail.com | No |
| `EMAIL_PORT` | SMTP port | 587 | No |
| `EMAIL_HOST_USER` | SMTP username | - | Yes (staging/prod) |
| `EMAIL_HOST_PASSWORD` | SMTP password | - | Yes (staging/prod) |
| `DEFAULT_FROM_EMAIL` | Default sender email | - | Yes (staging/prod) |

### Cache Variables (Staging/Production)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REDIS_URL` | Redis connection URL | - | Yes (staging/prod) |

## Troubleshooting

### Common Issues

#### 1. Import Errors with Models

If you see errors like `cannot import name 'User'`:
- Ensure you're using `settings.AUTH_USER_MODEL` for ForeignKey references
- Check that app names in `INSTALLED_APPS` match the AppConfig names

#### 2. Migration Issues

If migrations fail:
```bash
# Check migration status
python manage.py showmigrations

# Try fake migration (if DB is already up to date)
python manage.py migrate --fake

# Reset migrations (development only - data loss!)
rm db.sqlite3
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
python manage.py makemigrations
python manage.py migrate
```

#### 3. Environment Variables Not Loading

If environment variables aren't being recognized:
- Verify `.env` file exists in project root
- Check that `python-dotenv` is installed
- Ensure `.env` is not in `.gitignore` for your local copy
- Try explicitly loading: `export $(cat .env | xargs)`

#### 4. Port Already in Use

If port 8000 is already in use:
```bash
# Use a different port
python manage.py runserver 8080

# Or find and kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

#### 5. Static Files Not Loading

In development:
- Ensure `DEBUG=True`
- Django serves static files automatically in debug mode

In production:
```bash
python manage.py collectstatic
```

## Development Best Practices

### 1. Branch Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, commit
git add .
git commit -m "feat: your feature description"

# Push and create PR
git push origin feature/your-feature-name
```

### 2. Code Quality

```bash
# Format code
black .

# Check for issues
flake8 .

# Type checking
mypy .

# Security issues
bandit .
```

### 3. Environment Isolation

- Always use virtual environments
- Never commit `.env` files
- Keep `requirements.txt` updated
- Document new dependencies

### 4. Security

- Never commit secrets or API keys
- Use environment variables for sensitive data
- Keep `DJANGO_SECRET_KEY` secure and unique per environment
- Use HTTPS in production
- Keep dependencies updated

## Next Steps

1. **Explore the API**: Visit the Swagger UI to see all available endpoints
2. **Review Settings**: Read [SETTINGS_CONFIGURATION.md](SETTINGS_CONFIGURATION.md) for detailed environment configuration
3. **Run Tests**: Familiarize yourself with the test suite
4. **Join Development**: Check the project board for open issues and tasks

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Project README](../README.md)
- [Settings Configuration Guide](SETTINGS_CONFIGURATION.md)

## Getting Help

- Check existing documentation in the `documentation/` folder
- Review closed issues on GitHub
- Ask in the team chat or create a new issue

---

**Happy Coding! 🚀**
