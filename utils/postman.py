import requests
import json
from django.conf import settings
# from .security import log_audit

class PostmanAPI:
    """Utility class for interacting with Postman API."""
    
    def __init__(self):
        self.api_key = settings.POSTMAN_API_KEY
        self.workspace_id = settings.POSTMAN_WORKSPACE_ID
        self.collection_id = settings.POSTMAN_COLLECTION_ID
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
        # log_audit(None, "postman_collection_updated", {"collection_id": self.collection_id})
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
        # log_audit(None, "postman_collection_imported", {"workspace_id": self.workspace_id})
        return response.json()