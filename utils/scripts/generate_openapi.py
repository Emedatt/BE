"""
Generate OpenAPI 3.0 schema for the E-MEDATT authentication API.
"""

import sys
import os
import django
from django.core.management import call_command
from pathlib import Path


def generate_openapi_schema():
    """Generate OpenAPI schema and save to openapi.yaml."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    sys.path.append(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )  # Add project root to sys.path
    django.setup()
    output_path = Path("openapi.yaml")
    call_command("spectacular", "--file", str(output_path), "--format", "openapi")
    print(f"OpenAPI schema generated at {output_path}")


if __name__ == "__main__":
    generate_openapi_schema()
