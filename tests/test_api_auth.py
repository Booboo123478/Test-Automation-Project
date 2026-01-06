import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.mark.api
class TestUserRegistration:
    """Test user registration endpoint"""
    
    def test_register_with_valid_data(self, api_client, db):
        """User registration with valid data"""
        url = '/rest-auth/registration/'
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'key' in response.data
        assert User.objects.filter(username='newuser').exists()
    
    def test_register_with_mismatched_passwords(self, api_client, db):
        """Registration fails with mismatched passwords"""
        url = '/rest-auth/registration/'
        data = {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password1': 'Password123!',
            'password2': 'DifferentPass456!'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.filter(username='testuser2').exists()
    
    def test_register_with_weak_password(self, api_client, db):
        """Registration fails with weak password"""
        url = '/rest-auth/registration/'
        data = {
            'username': 'testuser3',
            'email': 'test3@example.com',
            'password1': '123',
            'password2': '123'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.filter(username='testuser3').exists()
    
    def test_register_with_duplicate_username(self, api_client, user):
        """Registration fails with duplicate username"""
        url = '/rest-auth/registration/'
        data = {
            'username': user.username,
            'email': 'different@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data or 'non_field_errors' in response.data


@pytest.mark.api
class TestUserLogin:
    """Test user login endpoint"""
    
    def test_login_with_valid_credentials(self, api_client, user):
        """User login with valid credentials"""
        url = '/rest-auth/login/'
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'key' in response.data
    
    def test_login_with_invalid_credentials(self, api_client, user):
        """Login fails with invalid credentials"""
        url = '/rest-auth/login/'
        data = {
            'username': 'testuser',
            'password': 'WrongPassword!'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.api
class TestUserLogout:
    """Test user logout endpoint"""
    
    def test_logout_authenticated_user(self, authenticated_client):
        """Authenticated user can logout"""
        url = '/rest-auth/logout/'
        
        response = authenticated_client.post(url)
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT, status.HTTP_400_BAD_REQUEST]
    

@pytest.mark.api
class TestUserProfile:
    """Test user profile and ID endpoints"""
    
    def test_get_user_id_authenticated(self, authenticated_client, user):
        """Authenticated user can get their user ID"""
        url = '/api/user-id/'
        
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['userID'] == user.id
    
    def test_get_user_id_unauthenticated(self, api_client):
        """Unauthenticated user cannot get user ID"""
        url = '/api/user-id/'
        
        response = api_client.get(url)
        
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
