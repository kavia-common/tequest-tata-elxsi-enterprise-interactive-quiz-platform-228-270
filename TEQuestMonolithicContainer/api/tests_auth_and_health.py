from rest_framework.test import APITestCase
from django.urls import reverse

class HealthTests(APITestCase):
    def test_health(self):
        url = reverse('Health')  # Make sure the URL is named
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "Server is up!"})

class RegistrationTests(APITestCase):
    def test_register(self):
        url = reverse('register')
        payload = {
            'username': 'john',
            'email': 'john@example.com',
            'password': 'StrongPass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'participant',
        }
        response = self.client.post(url, data=payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['username'], 'john')
