from __future__ import absolute_import, unicode_literals
from rest_framework import serializers

from .models import (
    Movie,
    Person,
    PersonRoles,
    MoviePeopleRoles,
)


class WritePeopleSerializer(serializers.ModelSerializer):
    people = serializers.JSONField(write_only=True, required=True)

    def is_valid(self, raise_exception=False):
        is_valid = super(WritePeopleSerializer, self).is_valid(raise_exception=raise_exception)
        return is_valid

    def validate(self, attrs):
        data = super(WritePeopleSerializer, self).validate(attrs)
        people = data.pop('people')

        if not isinstance(people, list) or list(filter(lambda x: not x.get('id') or not x.get('role_id'), people)):
            raise serializers.ValidationError({'people': ['Something was wrong on assigning Stuff to the Movie. '
                                                          'Please try again sending ID and ROLE_ID '
                                                          'fields on the right way.']})

        return data

    def update(self, instance, validated_data):
        people = validated_data['people']

        MoviePeopleRoles.objects.filter(movie=instance).delete()
        for person in people:
            MoviePeopleRoles.objects.create(movie=instance,
                                            person_role=PersonRoles.objects.create(person=person['id'],
                                                                                   role=person['role_id']))

        return instance


class WriteMovieSerializer(serializers.ModelSerializer):
    title = serializers.CharField(error_messages={'invalid': 'Invalid Title'}, write_only=True, required=True)
    release_year = serializers.DateField(write_only=True, required=True)
    people = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = Movie
        fields = ('title', 'release_year', 'people',)

    def is_valid(self, raise_exception=False):
        is_valid = super(WriteMovieSerializer, self).is_valid(raise_exception=raise_exception)
        return is_valid

    def create(self, validated_data):
        people = validated_data.pop('people') if validated_data.get('people', None) else None
        instance = Movie.objects.create(**validated_data)

        if people is not None:
            serializer = WritePeopleSerializer(instance=instance, data=people)
            serializer.is_valid(raise_exception=True)

        return instance

    def update(self, instance, validated_data):
        instance.title = validated_data.pop('title')
        instance.release_year = validated_data.pop('release_year')
        instance.save()

        people = validated_data.pop('people') if validated_data.get('people', None) else None
        if people is not None:
            serializer = WritePeopleSerializer(instance=instance, data=people)
            serializer.is_valid(raise_exception=True)

        return instance


class WriteRolesSerializer(serializers.ModelSerializer):
    roles = serializers.ListField( write_only=True, required=True, child=serializers.IntegerField())

    def is_valid(self, raise_exception=False):
        is_valid = super(WriteRolesSerializer, self).is_valid(raise_exception=raise_exception)
        return is_valid

    def validate(self, attrs):
        data = super(WriteRolesSerializer, self).validate(attrs)
        roles = data.pop('roles')

        if not isinstance(roles, list):
            raise serializers.ValidationError({'roles': ['Invalid Roles']})

    def update(self, instance, validated_data):
        roles = validated_data['roles']

        PersonRoles.objects.filter(person=instance).delete()
        for role in roles:
            PersonRoles.objects.create(person=instance, role=role)

        return instance


class WritePersonSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(error_messages={'invalid': 'Invalid First Name'}, write_only=True, required=True)
    last_name = serializers.CharField(error_messages={'invalid': 'Invalid Last Name'}, write_only=True, required=True)

    aliases = serializers.CharField(write_only=True, required=False)
    roles = serializers.ListField( write_only=True, required=False, child=serializers.IntegerField())

    class Meta:
        model = Person
        fields = ('first_name', 'last_name', 'aliases', 'roles')

    def is_valid(self, raise_exception=False):
        is_valid = super(WritePersonSerializer, self).is_valid(raise_exception=raise_exception)
        return is_valid

    def create(self, validated_data):
        roles = validated_data.pop('roles') if validated_data.get('roles', None) else None
        instance = Person.objects.create(**validated_data)

        if roles is not None:
            serializer = WriteRolesSerializer(instance=instance, data=roles)
            serializer.is_valid(raise_exception=True)

        return instance

    def update(self, instance, validated_data):
        instance.first_name = validated_data.pop('first_name')
        instance.last_name = validated_data.pop('last_name')
        instance.aliases = validated_data.pop('aliases')
        instance.save()

        roles = validated_data.pop('roles') if validated_data.get('roles', None) else None
        if roles is not None:
            serializer = WriteRolesSerializer(instance=instance, data=roles)
            serializer.is_valid(raise_exception=True)

        return instance


class PeopleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, source='person_role.person.id')
    person_role = serializers.CharField(read_only=True, source='person_role.__str__')

    class Meta:
        model = MoviePeopleRoles
        fields = ('id', 'person_role',)


class MovieSerializer(serializers.ModelSerializer):
    people = PeopleSerializer(many=True, read_only=True, source='people_roles')

    class Meta:
        model = Movie
        fields = ('id', 'title', 'release_year', 'people',)


class RolesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, source='role.id')
    name = serializers.CharField(read_only=True, source='role.name')

    class Meta:
        model = PersonRoles
        fields = ('id', 'name',)


class PersonSerializer(serializers.ModelSerializer):
    roles = RolesSerializer(many=True, read_only=True, source='people_roles')

    class Meta:
        model = Person
        fields = ('id', 'first_name', 'last_name', 'aliases', 'roles',)
