from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

def create_user():
    username = 'TestUsername'
    email = 'test@email.com'
    password = 'testpass123'
    new_user = get_user_model().objects.create(
        username=username,
        email=email
    )
    new_user.set_password(password)
    new_user.save()

    return new_user

def check_message(response, message):
    """Test if message is in the response"""

    messages = list(get_messages(response.wsgi_request))
    return any(msg.message == f"{message}" for msg in messages)



REGISTER_URL = reverse('register')
LOGIN_URL = reverse('login')
HOME_URL = reverse('home')
LOGOUT_URL = reverse('logout')


class TestRegisterView(TestCase):
    """Tests for register view"""

    def test_register_get_page(self):
        """Test register page"""
        response = self.client.get(REGISTER_URL)

        self.assertEqual(response.status_code, 200)

    def test_register_success(self):
        payload = {
            'username': 'Test Username',
            'email': 'test@example.com',
            'password': 'Testpass123',
            'confirm_password': 'Testpass123'
        }

        response = self.client.post(REGISTER_URL, payload)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

        query_user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(query_user.check_password(payload['password']))

    def test_register_missing_fields_error(self):
        payload = {
            'username': '',
            'email': '',
            'password': '',
            'confirm_password': ''
        }

        response = self.client.post(REGISTER_URL, payload)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, REGISTER_URL)

        self.assertTrue(check_message(response, "Error: Missing fields"))

        with self.assertRaises(get_user_model().DoesNotExist):
            get_user_model().objects.get(email=payload['email'])

    def test_passwords_dont_match_error(self):
        payload = {
            'username': 'Test Username',
            'email': 'test@example.com',
            'password': 'Testpass123',
            'confirm_password': 'Testpass'
        }

        response = self.client.post(REGISTER_URL, payload)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, REGISTER_URL)

        self.assertTrue(check_message(response, "Error: Passwords doesn't match"))

        with self.assertRaises(get_user_model().DoesNotExist):
            get_user_model().objects.get(email=payload['email'])
    

    def test_email_exists_error(self):
        user = create_user()
        
        payload = {
            'username': 'Test Username',
            'email': 'test@email.com',
            'password': 'Testpass123',
            'confirm_password': 'Testpass123'
        }

        response = self.client.post(REGISTER_URL, payload)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, REGISTER_URL)

        self.assertTrue(check_message(response, "Email already registered."))

        self.assertTrue(get_user_model().objects.filter(email=user.email).exists())

    def test_authenticated_user_redirected(self):
        user = create_user()

        self.client.force_login(user)

        response = self.client.get(REGISTER_URL)
        self.assertRedirects(response, REGISTER_URL)
        user = self.client.session.get('_auth_user_id')
        self.assertIsNone(user)


class TestLoginView(TestCase):
    """Tests for Login view"""

    def test_login_page_get_success(self):
        """Test get request"""
        response = self.client.get(LOGIN_URL)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_redirected_error(self):
        """Test if authenticated user is loged out and redirected"""
        user = create_user()
        self.client.force_login(user)

        user = self.client.session.get('_auth_user_id')
        self.assertIsNotNone(user)

        response = self.client.get(LOGIN_URL)
        self.assertRedirects(response, LOGIN_URL)

        user = self.client.session.get('_auth_user_id')
        self.assertIsNone(user)

    def test_login_success(self):
        user = create_user()

        payload = {
            'email': user.email,
            'password': 'testpass123'
        }

        response = self.client.post(LOGIN_URL, payload)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, HOME_URL)

    def test_login_wrong_email_error(self):
        user = create_user()

        payload = {
            'email': 'test123@example.com',
            'password': 'testpass123'
        }

        response = self.client.post(LOGIN_URL, payload)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, LOGIN_URL)
        self.assertTrue(check_message(response, "Invalid username and/or password."))

    def test_login_wrong_password_error(self):
        user = create_user()

        payload = { 
            'email': user.email,
            'password': 'testpass1234'
        }

        response = self.client.post(LOGIN_URL, payload)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, LOGIN_URL)
        self.assertTrue(check_message(response, "Invalid username and/or password."))

class TestLogoutView(TestCase):
    """Test logout View"""

    def test_logout_success(self):
        user = create_user()
        self.client.force_login(user)

        user = self.client.session.get('_auth_user_id')
        self.assertIsNotNone(user)

        self.client.get(LOGOUT_URL)

        user = self.client.session.get('_auth_user_id')
        self.assertIsNone(user)

    def test_logout_not_authenticated_error(self):
        self.client.get(LOGOUT_URL)