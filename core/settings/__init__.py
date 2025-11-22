"""
Django settings module loader.
Automatically loads the appropriate settings file based on DJANGO_ENVIRONMENT.
Valid values: 'development', 'staging', 'production'
Defaults to 'development' if not set.
"""

import os

# Get environment from environment variable, default to development
environment = os.getenv("DJANGO_ENVIRONMENT", "development").lower()

# Import settings based on environment
if environment == "production":
    from .production import *
elif environment == "staging":
    from .staging import *
else:
    # Default to development
    from .development import *

# Make the environment accessible
ENVIRONMENT = environment
