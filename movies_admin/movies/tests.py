from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django_dynamic_fixture import G
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from datetime import date

from .models import (
    Person,
    PersonRoles,
    Movie,
    Role,
)


class BaseTests(APITestCase):
    def setUp(self):
        super(BaseTests, self).setUp()

        self.user = User.objects.create_user(username='test', password='test1234')
        token = Token.objects.get_or_create(user=self.user)
        authorization = 'Token {}'.format(token)
        self.client.credentials(HTTP_AUTHORIZATION=authorization)

        self.roles = list(Role.objects.all().values_list('id', flat=True))


class PersonTests(BaseTests):
    def setUp(self):
        super(PersonTests, self).setUp()

        self.person_1 = G(Person, first_name='George', last_name='Lucas')
        self.person_2 = G(Person, first_name='Mark', last_name='Hamill')

    def test_get_people(self):
        """
        Ensure we can get a list of people.
        """
        self.client.logout()

        url = reverse('people-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_person(self):
        """
        Ensure we can get an existing person.
        """
        self.client.logout()

        url = reverse('people-detail', kwargs={'pk': self.person_1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_person(self):
        """
        Ensure we can create a new person object.
        """

        self.client.logout()
        self.client.force_login(self.user)

        url = reverse('people-list')
        data = {
            'first_name': 'Robert',
            'last_name': 'De Niro',
            'aliases': 'The Best',
            'roles': [self.roles[0], self.roles[2]]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['first_name'], 'Robert')
        self.assertEqual(len(response.data['roles']), 2)

    def test_update_person(self):
        """
        Ensure we can update an existing person object.
        """

        self.client.logout()
        self.client.force_login(self.user)

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

        self.client.logout()
        self.client.force_login(self.user)

        url = reverse('people-detail', kwargs={'pk': self.person_1.id})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class MovieTests(BaseTests):
    def setUp(self):
        super(MovieTests, self).setUp()

        self.movie_1 = G(Movie, title='Star Wars', release_year=date(1977, 10, 7))
        self.movie_2 = G(Movie, title='Indiana Jones', release_year=date(1983, 4, 7))

        self.people = []

        self.person_1 = G(Person, first_name='Sylvester', last_name='Stallone')
        self.person_2 = G(Person, first_name='Arnold', last_name='Schwarzenegger')

        self.person_role_1 = G(PersonRoles, person=self.person_1, role=self.roles[0])
        self.person_role_2 = G(PersonRoles, person=self.person_1, role=self.roles[1])
        self.person_role_3 = G(PersonRoles, person=self.person_2, role=self.roles[0])

        self.people.append(self.person_role_1.id)
        self.people.append(self.person_role_2.id)
        self.people.append(self.person_role_3.id)

    def test_get_movies(self):
        """
        Ensure we can get a list of movies.
        """
        self.client.logout()

        url = reverse('movies-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_movie(self):
        """
        Ensure we can get an existing movie.
        """
        self.client.logout()

        url = reverse('movies-detail', kwargs={'pk': self.movie_2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_movie(self):
        """
        Ensure we can create a new movie object.
        """

        self.client.logout()
        self.client.force_login(self.user)

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
        self.assertEqual(response.data['casting'], '{}, {}'.format(self.person_1, self.person_2))
        self.assertEqual(response.data['directors'], '{}'.format(self.person_1))

    def test_update_movie(self):
        """
        Ensure we can update an existing movie object.
        """

        self.client.logout()
        self.client.force_login(self.user)

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

        self.client.logout()
        self.client.force_login(self.user)

        url = reverse('movies-detail', kwargs={'pk': self.movie_1.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
