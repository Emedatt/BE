from django.contrib.auth import authenticate, login, logout
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from django.contrib.sessions.models import Session
from datetime import timedelta
from .models import User, PatientProfile, DoctorProfile, EmailVerificationToken, PasswordResetToken
from .serializers import (
    UserSerializer, PatientProfileSerializer, DoctorProfileSerializer,
    RegisterSerializer, AdminUserCreateSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, ChangePasswordSerializer, DeleteAccountSerializer
)
from .serializers_swagger import TokenResponseSerializer
from .permissions import IsPatient, IsDoctor, IsSuperuser
from .utils.security import log_audit
from .utils.notifications import send_verification_email, send_password_reset_email

class GetUserTokensView(APIView):
    """Temporary endpoint for development to retrieve user tokens"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Retrieve all tokens for a user (temporary endpoint for development)",
        manual_parameters=[
            openapi.Parameter(
                'email',
                openapi.IN_QUERY,
                description="User's email address",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: TokenResponseSerializer,
            404: openapi.Response(
                description="User not found",
                examples={"application/json": {"error": "User not found"}}
            )
        }
    )
    def get(self, request):
        email = request.query_params.get('email')
        try:
            user = User.objects.get(email=email)
            # Get or create verification token
            verification_token, _ = EmailVerificationToken.objects.get_or_create(
                user=user,
                defaults={'expires_at': timezone.now() + timedelta(hours=24)}
            )
            # Get or create password reset token
            reset_token, _ = PasswordResetToken.objects.get_or_create(
                user=user,
                defaults={'expires_at': timezone.now() + timedelta(hours=24)}
            )
            return Response({
                'email_verification_token': str(verification_token.token),
                'password_reset_token': str(reset_token.token),
                'message': 'Tokens retrieved successfully'
            })
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [UserRateThrottle]

    @swagger_auto_schema(
        operation_description="Register a new user (patient or doctor)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password', 'confirm_password', 'first_name', 'last_name', 'role'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format='password'),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, format='password'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                'role': openapi.Schema(type=openapi.TYPE_STRING, enum=['patient', 'doctor']),
            }
        ),
        responses={
            201: UserSerializer,
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "email": ["This field must be unique."],
                        "password": ["Password is too common."],
                        "confirm_password": ["Passwords must match."],
                        "role": ["Invalid role"]
                    }
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Create a new user account.

        parameters:
        - name: body
          description: User registration data
          required: true
          schema:
            type: object
            required:
              - email
              - password
              - confirm_password
              - first_name
              - last_name
              - role
            properties:
              email:
                type: string
                format: email
              password:
                type: string
                format: password
                minLength: 8
              confirm_password:
                type: string
                format: password
              first_name:
                type: string
              last_name:
                type: string
              role:
                type: string
                enum: [patient, doctor]

        responses:
          201:
            description: User created successfully
            content:
              application/json:
                example: {
                  "id": 1,
                  "email": "user@example.com",
                  "first_name": "John",
                  "last_name": "Doe",
                  "role": "patient",
                  "is_email_verified": false
                }
          400:
            description: Bad request (invalid data)
            content:
              application/json:
                examples:
                  invalid_password:
                    value: {
                      "password": ["Password must be at least 8 characters long"]
                    }
                  password_mismatch:
                    value: {
                      "confirm_password": ["Passwords must match"]
                    }
                  invalid_role:
                    value: {
                      "role": ["Invalid role"]
                    }
        """
        return super().post(request, *args, **kwargs)

class LoginView(APIView):
    """
    Log in a user.

    * Requires email verification
    * Uses session-based authentication
    * Rate limited to prevent brute force attacks
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [UserRateThrottle]

    @swagger_auto_schema(
        operation_description="Authenticate and log in a user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format='password'),
            }
        ),
        responses={
            200: UserSerializer,
            401: openapi.Response(
                description="Invalid credentials",
                examples={"application/json": {"error": "Invalid credentials"}}
            ),
            403: openapi.Response(
                description="Email not verified",
                examples={"application/json": {"error": "Email not verified"}}
            ),
            429: openapi.Response(
                description="Too many attempts",
                examples={"application/json": {"error": "Request was throttled"}}
            )
        }
    )
    def post(self, request):
        """
        Authenticate a user and log them in.
        """
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if not user.is_email_verified:
                log_audit(user, "login_failed", {"reason": "unverified_email"})
                return Response({"error": "Email not verified"}, status=status.HTTP_403_FORBIDDEN)
            login(request, user)
            log_audit(user, "login", {"email": user.email})
            return Response(UserSerializer(user).data)
        log_audit(None, "login_failed", {"email": email, "reason": "invalid_credentials"})
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    """
    Log out the current user.

    * Requires authentication
    * Invalidates current session
    * Creates audit log entry
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Log out the current user and end their session",
        responses={
            200: openapi.Response(
                description="Logout successful",
                examples={"application/json": {"message": "Logged out successfully"}}
            ),
            401: openapi.Response(
                description="Not authenticated",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            )
        }
    )
    def post(self, request):
        """
        End the current user session.
        This will log the user out and invalidate their session.
        """
        log_audit(request.user, "logout", {"email": request.user.email})
        logout(request)
        return Response({"message": "Logged out successfully"})

class PatientProfileView(generics.RetrieveUpdateAPIView):
    queryset = PatientProfile.objects.all()
    serializer_class = PatientProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]

    @swagger_auto_schema(
        operation_description="Get or update the current patient's profile",
        responses={
            200: PatientProfileSerializer,
            401: openapi.Response(
                description="Not authenticated",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Not a patient",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            )
        }
    )
    def get_object(self):
        return self.request.user.patient_profile

    def perform_update(self, serializer):
        serializer.save()
        log_audit(self.request.user, "patient_profile_update", {"email": self.request.user.email})

class DoctorProfileView(generics.RetrieveUpdateAPIView):
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    @swagger_auto_schema(
        operation_description="Get or update the current doctor's profile",
        responses={
            200: DoctorProfileSerializer,
            401: openapi.Response(
                description="Not authenticated",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Not a doctor",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            )
        }
    )
    def get_object(self):
        return self.request.user.doctor_profile

    def perform_update(self, serializer):
        serializer.save()
        log_audit(self.request.user, "doctor_profile_update", {"email": self.request.user.email})

class AdminUserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserCreateSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser, IsSuperuser]

    def perform_create(self, serializer):
        serializer.save()

class EmailVerificationView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Verify user's email address using verification token",
        manual_parameters=[
            openapi.Parameter(
                'token',
                openapi.IN_PATH,
                description="Email verification token",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Email verified successfully",
                examples={"application/json": {"message": "Email verified successfully"}}
            ),
            400: openapi.Response(
                description="Invalid or expired token",
                examples={"application/json": {"error": "Invalid or expired token"}}
            )
        }
    )
    def get(self, request, token):
        try:
            verification = EmailVerificationToken.objects.get(token=token, expires_at__gt=timezone.now())
            user = verification.user
            user.is_email_verified = True
            user.save()
            log_audit(user, "email_verified", {"email": user.email})
            verification.delete()
            return Response({"message": "Email verified successfully"})
        except EmailVerificationToken.DoesNotExist:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        token = PasswordResetToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        send_password_reset_email(user.email, token.token)
        log_audit(user, "password_reset_requested", {"email": user.email})
        return Response({"message": "Password reset link sent"})

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, token):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            token_obj = PasswordResetToken.objects.get(token=token, expires_at__gt=timezone.now())
            user = token_obj.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            log_audit(user, "password_reset_completed", {"email": user.email})
            token_obj.delete()
            return Response({"message": "Password reset successfully"})
        except PasswordResetToken.DoesNotExist:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        log_audit(user, "password_changed", {"email": user.email})
        return Response({"message": "Password changed successfully"})

class DeleteAccountView(generics.GenericAPIView):
    serializer_class = DeleteAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.is_active = False
        user.deleted_at = timezone.now()
        user.save()
        log_audit(user, "account_deleted", {"email": user.email})
        logout(request)
        return Response({"message": "Account deleted successfully"})

class SessionListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all active sessions for the current user",
        responses={
            200: UserSerializer(many=True),
            401: openapi.Response(
                description="Not authenticated",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            )
        }
    )
    def get_queryset(self):
        sessions = Session.objects.filter(expire_date__gt=timezone.now())
        user_sessions = [s for s in sessions if s.get_decoded().get('_auth_user_id') == str(self.request.user.id)]
        return [self.request.user] * len(user_sessions)

class SessionDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Terminate a specific session for the current user",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="Session ID to terminate",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Session terminated successfully",
                examples={"application/json": {"message": "Session terminated"}}
            ),
            401: openapi.Response(
                description="Not authenticated",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Unauthorized",
                examples={"application/json": {"error": "Unauthorized"}}
            ),
            404: openapi.Response(
                description="Session not found",
                examples={"application/json": {"error": "Session not found"}}
            )
        }
    )
    def delete(self, request, id):
        try:
            session = Session.objects.get(session_key=id, expire_date__gt=timezone.now())
            if session.get_decoded().get('_auth_user_id') == str(request.user.id):
                session.delete()
                log_audit(request.user, "session_terminated", {"email": request.user.email, "session_id": id})
                return Response({"message": "Session terminated"})
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        except Session.DoesNotExist:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
