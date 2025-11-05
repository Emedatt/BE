python -c "import yaml; from utils.postman import PostmanAPI; with open('openapi.yaml', 'r') as f: spec = yaml.safe_load(f); PostmanAPI().update_collection(spec)"
