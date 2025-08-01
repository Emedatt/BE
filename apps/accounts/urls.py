from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, PatientProfileView, DoctorProfileView,
    AdminUserCreateView, EmailVerificationView, PasswordResetRequestView,
    PasswordResetConfirmView, ChangePasswordView, DeleteAccountView,
    SessionListView, SessionDeleteView, GetUserTokensView
)

app_name = 'accounts'

urlpatterns = [
    # Development only endpoint - remove in production
    path('dev/tokens/', GetUserTokensView.as_view(), name='get-user-tokens'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/patient/', PatientProfileView.as_view(), name='patient-profile'),
    path('profile/doctor/', DoctorProfileView.as_view(), name='doctor-profile'),
    path('admin/create/', AdminUserCreateView.as_view(), name='admin-create'),
    path('verify-email/<str:token>/', EmailVerificationView.as_view(), name='verify-email'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/confirm/<str:token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    path('sessions/', SessionListView.as_view(), name='session-list'),
    path('sessions/<str:id>/', SessionDeleteView.as_view(), name='session-delete'),
]
