"""
Tests for accounts app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model"""
    
    def test_create_parent(self):
        """Test creating a parent user"""
        user = User.objects.create_user(
            phone_number='+998901234567',
            password='testpass123',
            user_type='parent',
            first_name='Test',
            last_name='Parent'
        )
        
        self.assertEqual(user.phone_number, '+998901234567')
        self.assertEqual(user.user_type, 'parent')
        self.assertIsNotNone(user.family_code)
        self.assertEqual(len(user.family_code), 6)
    
    def test_create_child(self):
        """Test creating a child user"""
        # First create parent
        parent = User.objects.create_user(
            phone_number='+998901234567',
            password='testpass123',
            user_type='parent'
        )
        
        # Create child with parent's family code
        child = User.objects.create_user(
            phone_number='+998901234568',
            password='testpass123',
            user_type='child',
            family_code=parent.family_code
        )
        
        self.assertEqual(child.user_type, 'child')
        self.assertEqual(child.family_code, parent.family_code)


class AuthenticationAPITest(APITestCase):
    """Test authentication endpoints"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_parent_registration(self):
        """Test parent registration"""
        data = {
            'phone_number': '+998901234567',
            'first_name': 'Test',
            'last_name': 'Parent',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'date_of_birth': '1985-05-15'
        }
        
        response = self.client.post('/api/accounts/register/parent/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('family_code', response.data)
        self.assertIn('user', response.data)
    
    def test_child_registration(self):
        """Test child registration"""
        # First create parent
        parent = User.objects.create_user(
            phone_number='+998901234567',
            password='testpass123',
            user_type='parent'
        )
        
        data = {
            'phone_number': '+998901234568',
            'first_name': 'Test',
            'last_name': 'Child',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'family_code': parent.family_code,
            'date_of_birth': '2010-03-20'
        }
        
        response = self.client.post('/api/accounts/register/child/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
    
    def test_login(self):
        """Test login"""
        # Create user
        user = User.objects.create_user(
            phone_number='+998901234567',
            password='testpass123',
            user_type='parent'
        )
        
        data = {
            'phone_number': '+998901234567',
            'password': 'testpass123'
        }
        
        response = self.client.post('/api/accounts/login/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
    
    def test_profile_access(self):
        """Test profile access"""
        # Create and login user
        user = User.objects.create_user(
            phone_number='+998901234567',
            password='testpass123',
            user_type='parent'
        )
        
        self.client.force_authenticate(user=user)
        
        response = self.client.get('/api/accounts/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], '+998901234567')
