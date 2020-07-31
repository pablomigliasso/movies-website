from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django_dynamic_fixture import G
from datetime import date

from .models import (
    Person,
    PersonRoles,
    Movie,
    Role,
)


class PersonTests(APITestCase):
    def setUp(self):
        super(PersonTests, self).setUp()

        self.person_1 = G(Person, first_name='George', last_name='Lucas')

        self.roles = list(Role.objects.exclude(name='Producer').all().values_list('id', flat=True))

    def test_create_person(self):
        """
        Ensure we can create a new person object.
        """

        url = reverse('people-list')
        data = {
            'first_name': 'Robert',
            'last_name': 'De Niro',
            'aliases': 'The Best',
            'roles': self.roles
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['first_name'], 'Robert')
        self.assertEqual(len(response.data['roles']), 2)

    def test_update_person(self):
        """
        Ensure we can update an existing person object.
        """

        url = reverse('people-detail', kwargs={'pk': self.person_1.id})
        data = {
            'first_name': 'George D.',
            'last_name': 'Lucas II',
            'aliases': 'The Big One'
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_person(self):
        """
        Ensure we can delete an existing person object.
        """

        url = reverse('people-detail', kwargs={'pk': self.person_1.id})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class MovieTests(APITestCase):
    def setUp(self):
        super(MovieTests, self).setUp()

        self.movie_1 = G(Movie, title='Star Wars', release_year=date(1977, 10, 7))

        self.people = []

        self.role_1 = Role.objects.filter(name='Actor/Actress').first()
        self.role_2 = Role.objects.filter(name='Producer').first()

        self.person_1 = G(Person, first_name='Sylvester', last_name='Stallone')
        self.person_2 = G(Person, first_name='Arnold', last_name='Schwarzenegger')

        self.person_role_1 = G(PersonRoles, person=self.person_1, role=self.role_1)
        self.person_role_2 = G(PersonRoles, person=self.person_1, role=self.role_2)
        self.person_role_3 = G(PersonRoles, person=self.person_2, role=self.role_1)

        self.people.append(self.person_role_1.id)
        self.people.append(self.person_role_2.id)
        self.people.append(self.person_role_3.id)

    def test_create_movie(self):
        """
        Ensure we can create a new movie object.
        """

        url = reverse('movies-list')
        data = {
            'title': 'The Expendables',
            'release_year': str(date(2008, 1, 14)),
            'people': self.people
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['title'], 'The Expendables')
        self.assertEqual(len(response.data['people']), 3)

    def test_update_movie(self):
        """
        Ensure we can update an existing movie object.
        """

        url = reverse('movies-detail', kwargs={'pk': self.movie_1.id})
        data = {
            'title': 'Start War II',
            'release_year': date(1977, 7, 7)
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_movie(self):
        """
        Ensure we can delete an existing movie object.
        """

        url = reverse('movies-detail', kwargs={'pk': self.movie_1.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
