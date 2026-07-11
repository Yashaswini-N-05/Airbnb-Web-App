from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.crypto import get_random_string
from .models import UserProfile

User = get_user_model()


class UserRegistrationTestCase(APITestCase):
    """Test user registration"""
    
    def setUp(self):
        self.register_url = reverse('users:user-register')
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'TestPassword123!',
            'password_confirm': 'TestPassword123!',
        }
    
    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data['data'])
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        
        # Check if profile was created
        user = User.objects.get(email='test@example.com')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
    
    def test_user_registration_password_mismatch(self):
        """Test registration with password mismatch"""
        self.user_data['password_confirm'] = 'DifferentPassword123!'
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        User.objects.create_user(
            email='test@example.com',
            username='existinguser',
            password='Password123!'
        )
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTestCase(APITestCase):
    """Test user login"""
    
    def setUp(self):
        self.login_url = reverse('users:user-login')
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )
        
    def test_user_login_success(self):
        """Test successful login"""
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            'email': 'test@example.com',
            'password': 'WrongPassword'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileTestCase(APITestCase):
    """Test user profile endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        self.profile_url = reverse('users:user-profile')
    
    def test_get_profile(self):
        """Test getting user profile"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_update_profile(self):
        """Test updating user profile"""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone': '+1234567890'
        }
        response = self.client.patch(self.profile_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.phone, '+1234567890')


class PasswordManagementTestCase(APITestCase):
    """Test password management endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        self.password_change_url = reverse('users:password-change')
    
    def test_password_change_success(self):
        """Test successful password change"""
        change_data = {
            'old_password': 'TestPassword123!',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!'
        }
        response = self.client.post(self.password_change_url, change_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if password was actually changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123!'))
    
    def test_password_change_wrong_old_password(self):
        """Test password change with wrong old password"""
        change_data = {
            'old_password': 'WrongPassword',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!'
        }
        response = self.client.post(self.password_change_url, change_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EmailVerificationTestCase(APITestCase):
    """Test email verification endpoints"""
    
    def setUp(self):
        self.verification_url = reverse('users:email-verify')
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPassword123!',
            first_name='Test',
            last_name='User',
            email_verification_token=get_random_string(50)
        )
    
    def test_email_verification_success(self):
        """Test successful email verification"""
        verification_data = {
            'token': self.user.email_verification_token
        }
        response = self.client.post(self.verification_url, verification_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)
        self.assertIsNone(self.user.email_verification_token)
    
    def test_email_verification_invalid_token(self):
        """Test email verification with invalid token"""
        verification_data = {
            'token': 'invalid_token'
        }
        response = self.client.post(self.verification_url, verification_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLogoutTestCase(APITestCase):
    """Test user logout"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        self.logout_url = reverse('users:user-logout')
    
    def test_user_logout_success(self):
        """Test successful logout"""
        logout_data = {
            'refresh': str(self.refresh)
        }
        response = self.client.post(self.logout_url, logout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProfileStatusTestCase(APITestCase):
    """Test profile status endpoint"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        self.status_url = reverse('users:profile-status')
    
    def test_profile_status(self):
        """Test getting profile completion status"""
        response = self.client.get(self.status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('completion_percentage', response.data['data'])
        self.assertIn('email_verified', response.data['data'])
        self.assertIn('missing_fields', response.data['data'])
