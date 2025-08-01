from rest_framework import serializers

class TokenResponseSerializer(serializers.Serializer):
    email_verification_token = serializers.CharField(required=False)
    password_reset_token = serializers.CharField(required=False)
    message = serializers.CharField()
