E-MEDATT Postman Documentation Automation Plan
This document outlines the implementation plan to automate updates to the Postman documentation for the E-MEDATT telehealth platform’s authentication API. The plan ensures that the Postman collection and documentation reflect the latest API schema changes in real-time, using an OpenAPI 3.0 specification generated from Django REST Framework (DRF). The solution integrates with a CI/CD pipeline, aligns with the 12-month launch timeline, and adheres to production-grade standards (Flake8 compliance, ≥90% test coverage, security-first approach).

1. Requirements Analysis
Objectives

Automatically update Postman documentation whenever the API schema (auth app endpoints) changes.
Generate an OpenAPI 3.0 specification from the Django project using drf-spectacular.
Sync the OpenAPI spec with Postman’s API Builder to update the associated collection and documentation.
Integrate the update process into the CI/CD pipeline (GitHub Actions).
Ensure security by protecting Postman API keys and limiting access to documentation.
Support compliance with HIPAA/NDPR by avoiding exposure of sensitive endpoints or data in public documentation.

User Stories (Inferred)

As an API developer, I want the Postman documentation to reflect the latest API changes without manual updates.
As a team lead, I want the documentation update process to be automated in the CI/CD pipeline to reduce maintenance overhead.
As a security officer, I want to ensure that sensitive API keys and endpoints are protected during the automation process.

Edge Cases

Breaking changes in the API schema (e.g., renamed endpoints) causing sync failures.
Invalid OpenAPI spec causing Postman import errors.
Rate limits on Postman API requests during CI/CD runs.
Conflicts between local and remote Postman collections.

Performance Impacts

Minimize CI/CD pipeline runtime by caching OpenAPI spec generation.
Optimize Postman API calls to avoid rate limit issues (e.g., 60 requests/minute for free plans).
Use asynchronous tasks for non-critical updates (e.g., documentation publishing).

Security Concerns

Protect Postman API keys using environment variables or a secrets manager.
Restrict public documentation to non-sensitive endpoints (e.g., exclude admin-only endpoints).
Log CI/CD actions for auditability without storing sensitive data.
Ensure HTTPS for all API interactions with Postman.


2. Architecture & Design
Approach

Generate OpenAPI Specification:
Use drf-spectacular to generate an OpenAPI 3.0 schema from the Django auth app.
Store the schema in the repository (openapi.yaml).


Sync with Postman:
Use Postman’s API to import the OpenAPI spec and update the collection.
Enable Postman’s auto-sync feature to keep the collection in sync with the schema.


Automate via CI/CD:
Configure a GitHub Actions workflow to run on code pushes, generating the OpenAPI spec and updating Postman.


Secure Access:
Store Postman API keys in GitHub Secrets.
Restrict documentation access to authorized team members or private workspaces.



Technology Stack

Django/DRF: Python 3.10, Django 4.2, DRF 3.15, drf-spectacular==0.27.
Postman: Postman API, API Builder, and private workspace.
CI/CD: GitHub Actions for automation.
Secrets Management: GitHub Secrets for Postman API key.
Logging: Django logging for audit trails.
Dependencies: requests==2.31 for API calls, PyYAML==6.0 for schema manipulation.

Design Patterns

Single Responsibility: Separate OpenAPI generation, Postman syncing, and CI/CD tasks into distinct scripts.
Modular Design: Encapsulate Postman API logic in a utility module (utils/postman.py).
Idempotency: Ensure CI/CD scripts handle duplicate runs gracefully (e.g., check for existing collections).

API Endpoints (Postman API)

PUT /api/collections/{collection_uid}: Update an existing Postman collection.
POST /api/collections: Create a new collection (if needed).
GET /api/collections: Retrieve collection details for validation.



3. Test Cases
Unit Tests (in tests/test_postman.py)

OpenAPI Generation:
Test generate_openapi.py produces a valid OpenAPI 3.0 schema.
Test schema includes all auth app endpoints with correct security definitions.


Postman API Interaction:
Test PostmanAPI.get_collection retrieves the correct collection.
Test PostmanAPI.update_collection updates the collection with the OpenAPI spec.
Test PostmanAPI.import_openapi creates a new collection if none exists.


Error Handling:
Test failure for invalid Postman API key.
Test failure for invalid OpenAPI spec.
Test rate limit handling (mock 429 response).



Integration Tests

Test end-to-end flow: generate OpenAPI spec, sync with Postman, and verify updated documentation.
Test CI/CD pipeline: simulate a push to main, ensure schema generation and Postman sync complete without errors.

Coverage

Use pytest-cov to ensure ≥90% coverage:pytest tests/test_postman.py --cov=emedatt.utils.postman --cov-report=html


Mock requests library to simulate Postman API responses.


5. Security Considerations

API Key Protection:
We stored POSTMAN_API_KEY in GitHub Secrets, never in source code.
Restricted access to Postman workspace to team members with Workspace Admin or API Admin roles.


Data Exposure:
We filtered sensitive endpoints (e.g., /auth/admin/create/) from public documentation using drf-spectacular’s SCHEMA_PATH_PREFIX.
Avoided including sensitive data (e.g., example responses with PII) in the OpenAPI spec.


Rate Limiting:
We handled Postman API rate limits (60 requests/minute for free plans) by implementing retry logic in PostmanAPI.


Audit Logging:
We logged Postman sync actions in AuditLog without storing sensitive data (e.g., API keys).


Compliance:
We ensured HIPAA/NDPR compliance by restricting documentation access to private workspaces and encrypting API keys.




6. Documentation

README.md (partial excerpt):
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


API Reference: The Postman collection includes detailed documentation for all auth endpoints, auto-generated from the OpenAPI spec.



7. Code Review & CI/CD

Git Branching: Use GitFlow (feature/postman-automation merged into develop).
CI Pipeline:
Lint with flake8 to ensure compliance.
Run tests with pytest to verify OpenAPI generation and Postman sync.
Scan with bandit for security issues in Python scripts.


Code Review Checklist:
Verify drf-spectacular schema accuracy.
Ensure Postman API key is not exposed in logs or source code.
Confirm test coverage ≥90%.
Validate HIPAA/NDPR compliance for documentation access.




8. Development Timeline

Sprint 1 (1 week): Install drf-spectacular, configure OpenAPI schema, and generate openapi.yaml.
Sprint 2 (1 week): Implement PostmanAPI utility and test manual sync.
Sprint 3 (1 week): Set up GitHub Actions workflow and test end-to-end automation.
Sprint 4 (1 week): Add tests, security measures, and documentation.


9. Dependencies

drf-spectacular==0.27
requests==2.31
PyYAML==6.0
Existing dependencies from authentication plan (e.g., django==4.2, djangorestframework==3.15).


10. Risks & Mitigations

Risk: Postman API rate limits causing CI/CD failures.
Mitigation: Implement retry logic with exponential backoff in PostmanAPI.


Risk: Breaking API changes causing sync issues.
Mitigation: Validate schema in CI/CD and notify developers of issues via GitHub Actions.


Risk: Exposure of sensitive endpoints in documentation.
Mitigation: Use drf-spectacular filters to exclude admin endpoints from the schema.


Risk: Unauthorized access to Postman workspace.
Mitigation: Restrict workspace to team members and use role-based access control.




11. Postman Setup Instructions

Install drf-spectacular:pip install drf-spectacular

Add to INSTALLED_APPS in settings.py:INSTALLED_APPS = [
    ...,
    "drf_spectacular",
]


Configure Postman:
Create a private workspace in Postman.
Generate an API key at https://go.postman.co/settings/me/api-keys.
Create an initial collection for the auth API.


Set Environment Variables:
Add POSTMAN_API_KEY, POSTMAN_WORKSPACE_ID, and POSTMAN_AUTH_COLLECTION_ID to GitHub Secrets and local .env.


Run Initial Schema Generation:python scripts/generate_openapi.py


Test Postman Sync:python -c "import yaml; from emedatt.utils.postman import PostmanAPI; with open('openapi.yaml', 'r') as f: spec = yaml.safe_load(f); PostmanAPI().update_collection(spec)"


Enable CI/CD:
Push postman_sync.yml to .github/workflows/.
Verify workflow runs on push to main or develop.




12. Metrics & Monitoring

Metrics:
Time to complete Postman sync in CI/CD pipeline.
Success rate of schema generation and Postman updates.
Number of documentation views in Postman workspace.


Monitoring:
Log sync actions in AuditLog for compliance.
Use GitHub Actions logs to debug failures.
Monitor Postman API rate limit usage via response headers.

