import pytest
from unittest.mock import patch
from django.test import TestCase
from utils.postman import PostmanAPI


@pytest.mark.django_db
class PostmanAPITests(TestCase):
    def setUp(self):
        self.postman = PostmanAPI()

    @patch("requests.get")
    def test_get_collection(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "collection": {"info": {"name": "Test"}}
        }
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
