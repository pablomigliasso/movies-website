from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from model_utils import Choices

DEFAULT_ROLE = 'Actor/Actress'
DIRECTOR_ROLE = 'Director'
PRODUCER_ROLE = 'Producer'

ROLE_CHOICES = Choices(
    DEFAULT_ROLE,
    DIRECTOR_ROLE,
    PRODUCER_ROLE,
)


def year_to_roman(num):
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num


class Role(models.Model):
    name = models.CharField(_('Name'), max_length=30, null=False, blank=False, choices=ROLE_CHOICES,
                            default=DEFAULT_ROLE, unique=True)

    class Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        db_table = 'movies_role'

    def __str__(self):
        return self.name


class PersonRoles(models.Model):
    person = models.ForeignKey('movies.Person', on_delete=models.CASCADE, related_name='people_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='people_roles')

    class Meta:
        db_table = 'movies_person_roles'

    def __str__(self):
        return '{person} - {role}'.format(person=self.person, role=self.role)


class MoviePeopleRoles(models.Model):
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE, related_name='people_roles')
    person_role = models.ForeignKey(PersonRoles, on_delete=models.CASCADE, related_name='people_movies')

    class Meta:
        db_table = 'movies_movie_people_roles'

    def __str__(self):
        return self.person_role.__str__()


class MovieManager(models.Manager):
    use_in_migrations = True

    def create_new_movie(self, data):
        people_ary = data.pop('people', [])

        movie = Movie.objects.create(**data)

        for person_id in people_ary:
            person = Person.objects.get(pk=int(person_id))
            for role in person.roles.all():
                person_role = PersonRoles.objects.filter(person=person, role=role).first()
                MoviePeopleRoles.objects.create(movie=movie, person_role=person_role)

        return movie


class Movie(models.Model):
    title = models.CharField(_('Title'), max_length=100, null=False, blank=False)
    release_year = models.DateField(null=False)

    people = models.ManyToManyField(PersonRoles, related_name='movies', through=MoviePeopleRoles)

    objects = MovieManager()

    class Meta:
        verbose_name = _('Movie')
        verbose_name_plural = _('Movies')

    def __str__(self):
        return '{title} ({year})'.format(title=self.title, year=year_to_roman(self.release_year.year))

    def staff(self, role_name):
        return ", ".join(person_role.person.__str__() for person_role in self.people.filter(role__name=role_name).all())

    @cached_property
    def casting(self):
        return self.staff(DEFAULT_ROLE)

    @cached_property
    def directors(self):
        return self.staff(DIRECTOR_ROLE)

    @cached_property
    def producers(self):
        return self.staff(PRODUCER_ROLE)


class PersonManager(models.Manager):
    use_in_migrations = True

    def create_new_person(self, data):
        roles_ary = data.pop('roles', [])

        person = Person.objects.create(**data)

        for role_id in roles_ary:
            PersonRoles.objects.create(person=person, role=Role.objects.get(pk=int(role_id)))

        return person


class Person(models.Model):
    first_name = models.CharField(_('First Name'), max_length=50, null=False, blank=False)
    last_name = models.CharField(_('Last Name'), max_length=50, null=False, blank=False)
    aliases = models.CharField(_('Aliases'), max_length=50, null=True, blank=True)

    roles = models.ManyToManyField(Role, related_name='people', through=PersonRoles)

    objects = PersonManager()

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('People')

    def __str__(self):
        return '{first_name} {last_name}'.format(first_name=self.first_name, last_name=self.last_name)

    def movies(self, role_name):
        return ", ".join(
            movie.__str__() for movie in Movie.objects.filter(people__role__name=role_name, people__person=self).all())

    @cached_property
    def movies_as_actor_or_actress(self):
        return self.movies(DEFAULT_ROLE)

    @cached_property
    def movies_as_director(self):
        return self.movies(DIRECTOR_ROLE)

    @cached_property
    def movies_as_producer(self):
        return self.movies(PRODUCER_ROLE)
