from __future__ import absolute_import, unicode_literals
from django.contrib import admin
from .models import (
    Person,
    Role,
    Movie,
)


class RolesInline(admin.TabularInline):
    model = Person.roles.through
    extra = 0
    verbose_name = "Role"
    verbose_name_plural = "Roles"


class PeopleInline(admin.TabularInline):
    model = Movie.people.through
    extra = 0
    verbose_name = "Person"
    verbose_name_plural = "People"


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = (RolesInline,)
    readonly_fields = ('movies_as_actor_or_actress', 'movies_as_director', 'movies_as_producer')
    list_display = ('__str__',)
    list_filter = ('roles',)
    ordering = ('first_name', 'last_name',)
    search_fields = ('first_name', 'last_name', 'aliases',)
    fields = ['first_name', 'last_name', 'aliases', 'movies_as_actor_or_actress', 'movies_as_director',
              'movies_as_producer']

    @staticmethod
    def movies_as_actor_or_actress(obj):
        return obj.movies_as_actor_or_actress

    @staticmethod
    def movies_as_director(obj):
        return obj.movies_as_director

    @staticmethod
    def movies_as_producer(obj):
        return obj.movies_as_producer


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    inlines = (PeopleInline, )
    readonly_fields = ('casting', 'directors', 'producers',)
    list_display = ('__str__',)
    list_filter = ('people',)
    ordering = ('title', 'release_year',)
    search_fields = ('title',)
    fields = ['title', 'release_year', 'casting', 'directors', 'producers',]

    @staticmethod
    def casting(obj):
        return obj.casting

    @staticmethod
    def directors(obj):
        return obj.directors

    @staticmethod
    def producers(obj):
        return obj.producers
