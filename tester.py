import yaml
from utils.postman import PostmanAPI

with open('openapi.yaml', 'r') as f:
    spec = yaml.safe_load(f)
    res = PostmanAPI().update_collection(spec)
    print(res)


# from django.conf import settings

# api_key = settings.POSTMAN_API_KEY
# workspace_id = settings.POSTMAN_WORKSPACE_ID
# collection_id = settings.POSTMAN_COLLECTION_ID

# print(f"Postman API Key: {api_key}")
# print(f"Postman Workspace ID: {workspace_id}")
# print(f"Postman Collection ID: {collection_id}")