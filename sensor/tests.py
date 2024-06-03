from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from sensor.models import Sensor, SensorStatus, SensorType
from user.models import User

class SensorAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='test@gmail.com',
            password='password',
        )
        self.sensor = Sensor.objects.create(
            title='sensor title',
            type=SensorType.OUTDOOR,
            status=SensorStatus.ACTIVE,
            model='sensor model',
            installation_date=timezone.now()
        )

    def test_get_sensors(self):
        self.client.force_authenticate(self.user)
        response = self.client.get('/api/sensors/', format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_sensors(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            '/api/sensors/',
            data={
                "title": "string",
                "type": "OUTDOOR",
                "status": "ACTIVE",
                "model": "string",
                "installation_date": "2024-06-03T07:59:14.609Z"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['title'], 'string')
        self.assertEqual(response.json()['type'], 'OUTDOOR')
        self.assertEqual(response.json()['model'], 'string')

    def test_update_sensors(self):
        self.client.force_authenticate(self.user)
        response = self.client.patch(
            f'/api/sensors/{self.sensor.id}/',
            data={
                "title": "new title",
            },
            params={'id': self.sensor.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.json()['title'], 'new title')

    def test_delete_sensors(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(
            f'/api/sensors/{self.sensor.id}/',
            data={
                "title": "new title",
            },
            params={'id': self.sensor.id}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)