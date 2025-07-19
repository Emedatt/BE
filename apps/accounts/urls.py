from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, ProfileView, LogoutView, PasswordResetRequestView, PasswordResetConfirmView, PasswordChangeView
from .onboardingviews import RegisterView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Swagger documentation for TokenRefreshView
# decorated_refresh_view = swagger_auto_schema(
#     operation_description="Get new access token using refresh token",
#     responses={
#         200: openapi.Response(
#             description="Token refresh successful",
#             schema=openapi.Schema(
#                 type=openapi.TYPE_OBJECT,
#                 properties={
#                     'access': openapi.Schema(type=openapi.TYPE_STRING)
#                 }
#             )
#         ),
#         401: 'Invalid refresh token'
#     }
# )(TokenRefreshView.as_view())

urlpatterns = [
    path('onboarding/register/', RegisterView.as_view(), name='register'),
    # path('onboarding/register/verify-email/', RegisterView.as_view(), name='verify_email'),
    # path('onboarding/register/resend-verification/', RegisterView.as_view(), name='resend_verification'),
    # path('onboarding/register/verify-email/<uuid:token>/', RegisterView.as_view(), name='verify_email_token'),

    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('profile/password-change/', PasswordChangeView.as_view(), name='password_change'),
    path('profile/', ProfileView.as_view(), name='profile'),
]