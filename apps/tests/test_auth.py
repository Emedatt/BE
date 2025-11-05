import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from apps.accounts.models import User, PatientProfile, DoctorProfile, EmailVerificationToken, PasswordResetToken
from datetime import timedelta

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def verified_patient():
    user = User.objects.create_user(
        email='patient@test.com',
        password='testpass123',
        first_name='Test',
        last_name='Patient',
        role='patient',
        is_email_verified=True
    )
    PatientProfile.objects.create(user=user)
    return user

@pytest.fixture
def verified_doctor():
    user = User.objects.create_user(
        email='doctor@test.com',
        password='testpass123',
        first_name='Test',
        last_name='Doctor',
        role='doctor',
        is_email_verified=True
    )
    DoctorProfile.objects.create(
        user=user,
        license_number='TEST-123',
        specialty='General'
    )
    return user

@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        email='admin@test.com',
        password='testpass123',
        first_name='Test',
        last_name='Admin',
        role='admin'
    )

@pytest.mark.django_db
class TestRegistration:
    def test_patient_registration(self, api_client):
        data = {
            'email': 'newpatient@test.com',
            'password': 'securepass123',
            'confirm_password': 'securepass123',
            'first_name': 'New',
            'last_name': 'Patient',
            'role': 'patient'
        }
        response = api_client.post(reverse('accounts:register'), data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email='newpatient@test.com').exists()
        assert PatientProfile.objects.filter(user__email='newpatient@test.com').exists()

    def test_doctor_registration(self, api_client):
        data = {
            'email': 'newdoctor@test.com',
            'password': 'securepass123',
            'confirm_password': 'securepass123',
            'first_name': 'New',
            'last_name': 'Doctor',
            'role': 'doctor'
        }
        response = api_client.post(reverse('accounts:register'), data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email='newdoctor@test.com').exists()
        assert DoctorProfile.objects.filter(user__email='newdoctor@test.com').exists()

    def test_admin_registration_blocked(self, api_client):
        data = {
            'email': 'newadmin@test.com',
            'password': 'securepass123',
            'confirm_password': 'securepass123',
            'first_name': 'New',
            'last_name': 'Admin',
            'role': 'admin'
        }
        response = api_client.post(reverse('accounts:register'), data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestAuthentication:
    def test_login_success(self, api_client, verified_patient):
        data = {
            'email': 'patient@test.com',
            'password': 'testpass123'
        }
        response = api_client.post(reverse('accounts:login'), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'patient@test.com'

    def test_login_unverified(self, api_client):
        user = User.objects.create_user(
            email='unverified@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='patient'
        )
        data = {
            'email': 'unverified@test.com',
            'password': 'testpass123'
        }
        response = api_client.post(reverse('accounts:login'), data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_logout(self, api_client, verified_patient):
        api_client.force_authenticate(user=verified_patient)
        response = api_client.post(reverse('accounts:logout'))
        assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
class TestProfiles:
    def test_patient_profile_access(self, api_client, verified_patient):
        api_client.force_authenticate(user=verified_patient)
        response = api_client.get(reverse('accounts:patient-profile'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['email'] == verified_patient.email

    def test_doctor_profile_access(self, api_client, verified_doctor):
        api_client.force_authenticate(user=verified_doctor)
        response = api_client.get(reverse('accounts:doctor-profile'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['email'] == verified_doctor.email

@pytest.mark.django_db
class TestEmailVerification:
    def test_email_verification_success(self, api_client):
        user = User.objects.create_user(
            email='toverify@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='patient'
        )
        token = EmailVerificationToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        response = api_client.get(reverse('accounts:verify-email', args=[token.token]))
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.is_email_verified

@pytest.mark.django_db
class TestPasswordReset:
    def test_password_reset_request(self, api_client, verified_patient):
        response = api_client.post(
            reverse('accounts:password-reset'),
            {'email': verified_patient.email}
        )
        assert response.status_code == status.HTTP_200_OK
        assert PasswordResetToken.objects.filter(user=verified_patient).exists()

    def test_password_reset_confirm(self, api_client, verified_patient):
        token = PasswordResetToken.objects.create(
            user=verified_patient,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        data = {
            'token': token.token,
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        response = api_client.post(
            reverse('accounts:password-reset-confirm', args=[token.token]),
            data
        )
        assert response.status_code == status.HTTP_200_OK
        verified_patient.refresh_from_db()
        assert verified_patient.check_password('newpass123')
