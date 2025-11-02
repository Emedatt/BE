# E-MEDATT Postman Documentation Automation Plan

This document outlines the implementation plan to automate updates to the Postman documentation for the E-MEDATT telehealth platform’s authentication API. The plan ensures that the Postman collection and documentation reflect the latest API schema changes in real-time, using an OpenAPI 3.0 specification generated from Django REST Framework (DRF). The solution integrates with a CI/CD pipeline, aligns with the 12-month launch timeline, and adheres to production-grade standards (Flake8 compliance, ≥90% test coverage, security-first approach).

---

## 1. Requirements Analysis

### Objectives
- Automatically update Postman documentation whenever the API schema (`auth` app endpoints) changes.
- Generate an OpenAPI 3.0 specification from the Django project using `drf-spectacular`.
- Sync the OpenAPI spec with Postman’s API Builder to update the associated collection and documentation.
- Integrate the update process into the CI/CD pipeline (GitHub Actions).
- Ensure security by protecting Postman API keys and limiting access to documentation.
- Support compliance with HIPAA/NDPR by avoiding exposure of sensitive endpoints or data in public documentation.

### User Stories (Inferred)
- As an API developer, I want the Postman documentation to reflect the latest API changes without manual updates.
- As a team lead, I want the documentation update process to be automated in the CI/CD pipeline to reduce maintenance overhead.
- As a security officer, I want to ensure that sensitive API keys and endpoints are protected during the automation process.

### Edge Cases
- Breaking changes in the API schema (e.g., renamed endpoints) causing sync failures.
- Invalid OpenAPI spec causing Postman import errors.
- Rate limits on Postman API requests during CI/CD runs.
- Conflicts between local and remote Postman collections.

### Performance Impacts
- Minimize CI/CD pipeline runtime by caching OpenAPI spec generation.
- Optimize Postman API calls to avoid rate limit issues (e.g., 60 requests/minute for free plans).
- Use asynchronous tasks for non-critical updates (e.g., documentation publishing).

### Security Concerns
- Protect Postman API keys using environment variables or a secrets manager.
- Restrict public documentation to non-sensitive endpoints (e.g., exclude admin-only endpoints).
- Log CI/CD actions for auditability without storing sensitive data.
- Ensure HTTPS for all API interactions with Postman.

---

## 2. Architecture & Design

### Approach
1. **Generate OpenAPI Specification**:
   - Use `drf-spectacular` to generate an OpenAPI 3.0 schema from the Django `auth` app.
   - Store the schema in the repository (`openapi.yaml`).
2. **Sync with Postman**:
   - Use Postman’s API to import the OpenAPI spec and update the collection.
   - Enable Postman’s auto-sync feature to keep the collection in sync with the schema.
3. **Automate via CI/CD**:
   - Configure a GitHub Actions workflow to run on code pushes, generating the OpenAPI spec and updating Postman.
4. **Secure Access**:
   - Store Postman API keys in GitHub Secrets.
   - Restrict documentation access to authorized team members or private workspaces.

### Technology Stack
- **Django/DRF**: Python 3.10, Django 4.2, DRF 3.15, `drf-spectacular==0.27`.
- **Postman**: Postman API, API Builder, and private workspace.
- **CI/CD**: GitHub Actions for automation.
- **Secrets Management**: GitHub Secrets for Postman API key.
- **Logging**: Django logging for audit trails.
- **Dependencies**: `requests==2.31` for API calls, `PyYAML==6.0` for schema manipulation.

### Design Patterns
- **Single Responsibility**: Separate OpenAPI generation, Postman syncing, and CI/CD tasks into distinct scripts.
- **Modular Design**: Encapsulate Postman API logic in a utility module (`utils/postman.py`).
- **Idempotency**: Ensure CI/CD scripts handle duplicate runs gracefully (e.g., check for existing collections).

### API Endpoints (Postman API)
- `PUT /api/collections/{collection_uid}`: Update an existing Postman collection.
- `POST /api/collections`: Create a new collection (if needed).
- `GET /api/collections`: Retrieve collection details for validation.

---

## 3. Implementation Details

### File Structure
```
emedatt/
├── apps/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── permissions.py
├── utils/
│   ├── postman.py         # Postman API interaction utilities
│   ├── notifications.py
│   └── security.py
├── scripts/
│   ├── generate_openapi.py # Script to generate OpenAPI spec
├── tests/
│   ├── test_auth.py
│   ├── test_postman.py    # Tests for Postman automation
├── .github/
│   ├── workflows/
│   │   └── postman_sync.yml # CI/CD workflow for Postman sync
├── openapi.yaml           # Generated OpenAPI schema
├── settings.py
├── urls.py
├── requirements.txt
├── .flake8
├── pytest.ini
└── README.md
```

### Code Snippets

#### settings.py (Update)
```python
# Postman configuration
POSTMAN_API_KEY = os.getenv("POSTMAN_API_KEY")
POSTMAN_WORKSPACE_ID = os.getenv("POSTMAN_WORKSPACE_ID", "your-workspace-id")
POSTMAN_AUTH_COLLECTION_ID = os.getenv("POSTMAN_AUTH_COLLECTION_ID", "your-collection-id")

# drf-spectacular configuration
SPECTACULAR_SETTINGS = {
    "TITLE": "E-MEDATT Authentication API",
    "DESCRIPTION": "API for user authentication and profile management in the E-MEDATT telehealth platform.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": True,
    "SECURITY": [{"BearerAuth": []}],
    "SCHEMA_PATH_PREFIX": "/api/auth/",
    "ENUM_NAME_OVERRIDES": {
        "UserRole": "emedatt.apps.auth.models.User.role",
    },
}
```

#### urls.py (Update)
```python
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("auth/", include("emedatt.apps.auth.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
```

#### scripts/generate_openapi.py
```python
#!/usr/bin/env python
"""
Generate OpenAPI 3.0 schema for the E-MEDATT authentication API.
"""
import os
import django
from django.core.management import call_command
from pathlib import Path

def generate_openapi_schema():
    """Generate OpenAPI schema and save to openapi.yaml."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emedatt.settings")
    django.setup()
    output_path = Path("openapi.yaml")
    call_command("spectacular", "--file", str(output_path), "--format", "openapi")
    print(f"OpenAPI schema generated at {output_path}")

if __name__ == "__main__":
    generate_openapi_schema()
```

#### utils/postman.py
```python
import requests
import json
from django.conf import settings
from emedatt.utils.security import log_audit

class PostmanAPI:
    """Utility class for interacting with Postman API."""
    
    def __init__(self):
        self.api_key = settings.POSTMAN_API_KEY
        self.workspace_id = settings.POSTMAN_WORKSPACE_ID
        self.collection_id = settings.POSTMAN_AUTH_COLLECTION_ID
        self.base_url = "https://api.getpostman.com"
        self.headers = {"X-Api-Key": self.api_key}

    def get_collection(self):
        """Retrieve the current collection."""
        response = requests.get(
            f"{self.base_url}/collections/{self.collection_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def update_collection(self, openapi_spec: dict):
        """Update the Postman collection with the OpenAPI spec."""
        payload = {
            "collection": {
                "info": {
                    "name": "E-MEDATT Authentication API",
                    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
                },
                "item": openapi_spec.get("paths", {})
            }
        }
        response = requests.put(
            f"{self.base_url}/collections/{self.collection_id}",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        log_audit(None, "postman_collection_updated", {"collection_id": self.collection_id})
        return response.json()

    def import_openapi(self, openapi_spec: dict):
        """Import OpenAPI spec to create or update a collection."""
        payload = {
            "type": "openapi3",
            "input": openapi_spec
        }
        response = requests.post(
            f"{self.base_url}/collections?workspace={self.workspace_id}",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        log_audit(None, "postman_collection_imported", {"workspace_id": self.workspace_id})
        return response.json()
```

#### .github/workflows/postman_sync.yml
```yaml
name: Sync Postman Documentation
on:
  push:
    branches:
      - main
      - develop
  pull_request:
    branches:
      - main
      - develop

jobs:
  sync-postman:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Generate OpenAPI schema
        run: python scripts/generate_openapi.py
      - name: Sync Postman collection
        env:
          POSTMAN_API_KEY: ${{ secrets.POSTMAN_API_KEY }}
          POSTMAN_WORKSPACE_ID: ${{ secrets.POSTMAN_WORKSPACE_ID }}
          POSTMAN_AUTH_COLLECTION_ID: ${{ secrets.POSTMAN_AUTH_COLLECTION_ID }}
        run: |
          python -c "
          import yaml
          from emedatt.utils.postman import PostmanAPI
          with open('openapi.yaml', 'r') as f:
              spec = yaml.safe_load(f)
          postman = PostmanAPI()
          postman.update_collection(spec)
          "
      - name: Upload OpenAPI artifact
        uses: actions/upload-artifact@v3
        with:
          name: openapi-schema
          path: openapi.yaml
```

#### tests/test_postman.py
```python
import pytest
from unittest.mock import patch
from django.test import TestCase
from emedatt.utils.postman import PostmanAPI

@pytest.mark.django_db
class PostmanAPITests(TestCase):
    def setUp(self):
        self.postman = PostmanAPI()

    @patch("requests.get")
    def test_get_collection(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"collection": {"info": {"name": "Test"}}}
        result = self.postman.get_collection()
        assert result["collection"]["info"]["name"] == "Test"
        mock_get.assert_called_once()

    @patch("requests.put")
    def test_update_collection(self, mock_put):
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = {"collection": {"id": "test-id"}}
        spec = {"paths": {"/auth/login": {"post": {}}}}
        result = self.postman.update_collection(spec)
        assert result["collection"]["id"] == "test-id"
        mock_put.assert_called_once()

    @patch("requests.post")
    def test_import_openapi(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"collection": {"id": "new-id"}}
        spec = {"openapi": "3.0.0", "paths": {}}
        result = self.postman.import_openapi(spec)
        assert result["collection"]["id"] == "new-id"
        mock_post.assert_called_once()
```

---

## 4. Test Cases

### Unit Tests (in `tests/test_postman.py`)
- **OpenAPI Generation**:
  - Test `generate_openapi.py` produces a valid OpenAPI 3.0 schema.
  - Test schema includes all `auth` app endpoints with correct security definitions.
- **Postman API Interaction**:
  - Test `PostmanAPI.get_collection` retrieves the correct collection.
  - Test `PostmanAPI.update_collection` updates the collection with the OpenAPI spec.
  - Test `PostmanAPI.import_openapi` creates a new collection if none exists.
- **Error Handling**:
  - Test failure for invalid Postman API key.
  - Test failure for invalid OpenAPI spec.
  - Test rate limit handling (mock 429 response).

### Integration Tests
- Test end-to-end flow: generate OpenAPI spec, sync with Postman, and verify updated documentation.
- Test CI/CD pipeline: simulate a push to `main`, ensure schema generation and Postman sync complete without errors.

### Coverage
- Use `pytest-cov` to ensure ≥90% coverage:
  ```bash
  pytest tests/test_postman.py --cov=emedatt.utils.postman --cov-report=html
  ```
- Mock `requests` library to simulate Postman API responses.

---

## 5. Security Considerations
- **API Key Protection**:
  - Store `POSTMAN_API_KEY` in GitHub Secrets, never in source code.
  - Restrict access to Postman workspace to team members with `Workspace Admin` or `API Admin` roles.
- **Data Exposure**:
  - Filter sensitive endpoints (e.g., `/auth/admin/create/`) from public documentation using `drf-spectacular`’s `SCHEMA_PATH_PREFIX`.
  - Avoid including sensitive data (e.g., example responses with PII) in the OpenAPI spec.
- **Rate Limiting**:
  - Handle Postman API rate limits (60 requests/minute for free plans) by implementing retry logic in `PostmanAPI`.
- **Audit Logging**:
  - Log Postman sync actions in `AuditLog` without storing sensitive data (e.g., API keys).
- **Compliance**:
  - Ensure HIPAA/NDPR compliance by restricting documentation access to private workspaces and encrypting API keys.

---

## 6. Documentation
- **README.md** (partial excerpt):
  ```markdown
  # E-MEDATT Postman Documentation Automation

  ## Setup
  1. Install dependencies: `pip install -r requirements.txt`.
  2. Configure environment variables:
     - `POSTMAN_API_KEY`: Your Postman API key.
     - `POSTMAN_WORKSPACE_ID`: Your Postman workspace ID.
     - `POSTMAN_AUTH_COLLECTION_ID`: The ID of the authentication API collection.
  3. Generate OpenAPI schema: `python scripts/generate_openapi.py`.
  4. Sync with Postman: Triggered automatically via GitHub Actions on push to `main` or `develop`.

  ## CI/CD
  - GitHub Actions workflow (`postman_sync.yml`) generates the OpenAPI schema and syncs with Postman.
  - Artifacts (`openapi.yaml`) are uploaded for debugging.

  ## Accessing Documentation
  - View in Postman private workspace (requires team access).
  - Public documentation (if enabled) available via Postman’s “Publish Docs” feature.
  ```

- **API Reference**: The Postman collection includes detailed documentation for all `auth` endpoints, auto-generated from the OpenAPI spec.

---

## 7. Code Review & CI/CD
- **Git Branching**: Use GitFlow (`feature/postman-automation` merged into `develop`).
- **CI Pipeline**:
  - Lint with `flake8` to ensure compliance.
  - Run tests with `pytest` to verify OpenAPI generation and Postman sync.
  - Scan with `bandit` for security issues in Python scripts.
- **Code Review Checklist**:
  - Verify `drf-spectacular` schema accuracy.
  - Ensure Postman API key is not exposed in logs or source code.
  - Confirm test coverage ≥90%.
  - Validate HIPAA/NDPR compliance for documentation access.

---

## 8. Development Timeline
- **Sprint 1 (1 week)**: Install `drf-spectacular`, configure OpenAPI schema, and generate `openapi.yaml`.
- **Sprint 2 (1 week)**: Implement `PostmanAPI` utility and test manual sync.
- **Sprint 3 (1 week)**: Set up GitHub Actions workflow and test end-to-end automation.
- **Sprint 4 (1 week)**: Add tests, security measures, and documentation.

---

## 9. Dependencies
- `drf-spectacular==0.27`
- `requests==2.31`
- `PyYAML==6.0`
- Existing dependencies from authentication plan (e.g., `django==4.2`, `djangorestframework==3.15`).

---

## 10. Risks & Mitigations
- **Risk**: Postman API rate limits causing CI/CD failures.
  - **Mitigation**: Implement retry logic with exponential backoff in `PostmanAPI`.
- **Risk**: Breaking API changes causing sync issues.
  - **Mitigation**: Validate schema in CI/CD and notify developers of issues via GitHub Actions.
- **Risk**: Exposure of sensitive endpoints in documentation.
  - **Mitigation**: Use `drf-spectacular` filters to exclude admin endpoints from the schema.
- **Risk**: Unauthorized access to Postman workspace.
  - **Mitigation**: Restrict workspace to team members and use role-based access control.

---

## 11. Setup Instructions
1. **Install `drf-spectacular`**:
   ```bash
   pip install drf-spectacular
   ```
   Add to `INSTALLED_APPS` in `settings.py`:
   ```python
   INSTALLED_APPS = [
       ...,
       "drf_spectacular",
   ]
   ```
2. **Configure Postman**:
   - Create a private workspace in Postman.
   - Generate an API key at `https://go.postman.co/settings/me/api-keys`.
   - Create an initial collection for the `auth` API.
3. **Set Environment Variables**:
   - Add `POSTMAN_API_KEY`, `POSTMAN_WORKSPACE_ID`, and `POSTMAN_AUTH_COLLECTION_ID` to GitHub Secrets and local `.env`.
4. **Run Initial Schema Generation**:
   ```bash
   python scripts/generate_openapi.py
   ```
5. **Test Postman Sync**:
   ```bash
   python -c "import yaml; from emedatt.utils.postman import PostmanAPI; with open('openapi.yaml', 'r') as f: spec = yaml.safe_load(f); PostmanAPI().update_collection(spec)"
   ```
6. **Enable CI/CD**:
   - Push `postman_sync.yml` to `.github/workflows/`.
   - Verify workflow runs on push to `main` or `develop`.

---

## 12. Metrics & Monitoring
- **Metrics**:
  - Time to complete Postman sync in CI/CD pipeline.
  - Success rate of schema generation and Postman updates.
  - Number of documentation views in Postman workspace.
- **Monitoring**:
  - Log sync actions in `AuditLog` for compliance.
  - Use GitHub Actions logs to debug failures.
  - Monitor Postman API rate limit usage via response headers.

---

## 13. Next Steps
- **Stakeholder Review**: Validate the automation plan with the E-MEDATT team.
- **Initial Setup**: Configure Postman workspace and API key, then test manual sync.
- **CI/CD Deployment**: Enable GitHub Actions workflow and monitor first runs.
- **Feedback Loop**: Collect feedback from developers on documentation accuracy and usability.

This plan ensures that Postman documentation for the E-MEDATT authentication API is automatically updated with every schema change, maintaining accuracy and reducing manual effort while adhering to security and compliance standards.