import os
from dotenv import load_dotenv
from django.test import TestCase
from django.conf import settings

load_dotenv() 

class EnvVariablesTestCase(TestCase):
    def test_env_variables_set(self):
        """
        Test that required environment variables are set.
        """
        required_env_vars = [
            'EMAIL_HOST_USER',
            'EMAIL_HOST_PASSWORD',
            'DEFAULT_FROM_EMAIL',
            'FRONTEND_URL',
        ]

        for var in required_env_vars:
            with self.subTest(var=var):
                self.assertIsNotNone(os.environ.get(var), f"{var} is not set in .env")

