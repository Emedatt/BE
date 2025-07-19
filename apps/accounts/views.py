from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserLoginSerializer, UserSerializer, ProfileSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer, PasswordChangeSerializer, LogoutSerializer
from .models import User

class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    @swagger_auto_schema(
        operation_description="Login with email and password",
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'tokens': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                                'access': openapi.Schema(type=openapi.TYPE_STRING),
                                'access_expires_at': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        ),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            401: 'Unauthorized'
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({
            'tokens': serializer.validated_data['tokens'],
            'user': UserSerializer(serializer.validated_data['user']).data
        })

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    @swagger_auto_schema(
        operation_description="Get current user profile",
        responses={200: ProfileSerializer}
    )
    def get_object(self):
        return self.request.user.profile

class LogoutView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LogoutSerializer

    @swagger_auto_schema(
        operation_description="Blacklist refresh token to logout user",
        request_body=LogoutSerializer,
        responses={200: 'OK', 400: 'Bad Request'}
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetRequestSerializer

    @swagger_auto_schema(
        operation_description="Request password reset email",
        request_body=PasswordResetRequestSerializer,
        responses={200: 'OK', 400: 'Bad Request'}
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()

        if user:
            # Generate token and send email (placeholder for now)
            # In a real application, you would generate a token and send a password reset email.
            # For example, using Django's PasswordResetTokenGenerator
            # from django.contrib.auth.tokens import PasswordResetTokenGenerator
            # token = PasswordResetTokenGenerator().make_token(user)
            # uid = urlsafe_base64_encode(force_bytes(user.pk))
            # reset_url = f"http://localhost:8000/reset-password/{uid}/{token}/"
            # send_mail(
            #     'Password Reset Request',
            #     f'Click the link to reset your password: {reset_url}',
            #     'from@example.com',
            #     [email],
            #     fail_silently=False,
            # )
            pass

        return Response({'message': 'If an account with that email exists, we have sent instructions.'}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetConfirmSerializer

    @swagger_auto_schema(
        operation_description="Confirm password reset with UID and token",
        request_body=PasswordResetConfirmSerializer,
        responses={200: 'OK', 400: 'Bad Request'}
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'The reset link is invalid or has expired.'}, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordChangeSerializer

    @swagger_auto_schema(
        operation_description="Change authenticated user's password",
        request_body=PasswordChangeSerializer,
        responses={200: 'OK', 400: 'Bad Request'}
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
            return Response({'old_password': ['Wrong password.']}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)
