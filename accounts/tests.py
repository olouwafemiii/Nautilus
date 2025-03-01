from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class UserViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="User",
        )
        self.superuser = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpassword123",
            first_name="Admin",
            last_name="User",

        )
        self.client.force_authenticate(user=self.user)  # Authenticate the client

    def test_retrieve_user(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse('user-detail', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse('user-detail', args=[self.user.id])
        data = {'first_name': 'Updated'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_user(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse('user-detail', args=[self.user.id])
        data = {'last_name': 'Updated'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_destroy_user(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse('user-detail', args=[self.user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_me_endpoint(self):
        url = reverse('user-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
