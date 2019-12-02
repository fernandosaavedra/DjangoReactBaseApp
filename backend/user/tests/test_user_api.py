from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')
CHANGE_PW_URL = reverse('user:change_password')
PW_RECOVERY = reverse('user:password_recovery')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def sample_user(email='test@test.com', password='testpassword',
                first_name='Test', last_name='User'):
    """ Return test user for insert new user """
    user = {'email': email, 'password': password,
            'first_name': first_name, 'last_name': last_name}
    return user


def sample_token_user(email='test@test.com', password='testpassword'):
    """ Return test payload for login """
    token_user = {'email': email, 'password': password}
    return token_user


class PublicUserApiTests(TestCase):
    """ Test the users API Public """
    def setUp(self):
        self.user = create_user(**sample_user(email='test2@test.com'))
        self.client = APIClient()

    def test_create_token_for_user(self):
        """ Test that a token is created for the user """
        payload = sample_user()
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given """
        create_user(**sample_token_user())
        payload = sample_token_user(password='wrong')
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """ Test that token is not created if user doesn't exist"""
        payload = sample_token_user()
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """ Test that email and password are required """
        payload = sample_token_user(password='')
        res = self.client.post(
            TOKEN_URL, payload
        )
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_profile_unauthorized(self):
        """ Test that authentication is required for users """
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_user_password_unauthorized(self):
        """ Test that change user password is required for users """
        payload = {'old_password': 'testpassword', 'new_password': '12345',
                   'new_password2': '12345'}
        res = self.client.patch(CHANGE_PW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_recovery_successfully_user_exists(self):
        """ Test recovering password succesfully when user exists """
        payload = {'email': self.user.email}
        old_pw = self.user.password
        res = self.client.post(PW_RECOVERY, payload)
        self.user.refresh_from_db()
        new_pw = self.user.password
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotEqual(old_pw, new_pw)

    def test_password_recovery_successfully_user_not_exists(self):
        """ Test recovering password succesfully when user not exists"""
        payload = {'email': 'fsaavedraolmos2@gmail.com'}
        res = self.client.post(PW_RECOVERY, payload)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class PrivateUserApiTests(TestCase):
    """ Test API request that require authentication """
    def setUp(self):
        self.user = create_user(**sample_user())
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """ Test retrieving profile for logged in used """
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """ Test that POST is not allowed on the me url """
        res = self.client.post(ME_URL, {})
        self.assertEqual(
            res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_update_user_profile(self):
        """ Test updating the user profile for authenticated user """
        payload = sample_user(first_name='test2', last_name='test2',
                              password='1234567',  email='testing@test.cl')
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload['password']))
        for key in payload.keys():
            if key is not 'password':
                self.assertEqual(payload[key], getattr(self.user, key))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_change_password_fails_passwords_do_not_match(self):
        """ Test changing the user password fails because passwords
            not match """
        payload = {'old_password': 'testpassword', 'new_password': '12345',
                   'new_password2': '123456'}
        res = self.client.patch(CHANGE_PW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['new_password'][0],
                         'Passwords do not match.')

    def test_change_password_fails_wrong_old_password(self):
        """ Test changing the user password fails because old_password
            is wrong """
        payload = {'old_password': 'testpassword123',
                   'new_password': '12345', 'new_password2': '123456'}
        res = self.client.patch(CHANGE_PW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['old_password'][0],
                         'Wrong password.')

    def test_change_password_success(self):
        """ Test changing the user password for authenticated user """
        old_password = self.user.password
        payload = {'old_password': 'testpassword', 'new_password': '12345',
                   'new_password2': '12345'}
        res = self.client.patch(CHANGE_PW_URL, payload)
        new_password = self.user.password
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotEqual(old_password, new_password)
