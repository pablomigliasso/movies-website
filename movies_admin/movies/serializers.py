from __future__ import absolute_import, unicode_literals
from rest_framework import serializers

from .models import (
    Movie,
    Person,
    PersonRoles,
    MoviePeopleRoles,
    Role,
)


class WritePeopleSerializer(serializers.Serializer):
    people = serializers.ListField(write_only=True, required=True, min_length=1,
                                   child=serializers.PrimaryKeyRelatedField(queryset=PersonRoles.objects.all(),
                                                                            write_only=True,
                                                                            required=True))

    def validate(self, attrs):
        data = super(WritePeopleSerializer, self).validate(attrs)
        people = data['people']

        if not isinstance(people, list):
            raise serializers.ValidationError({'people': ['Invalid People']})

        return data

    def save(self, **kwargs):
        movie = kwargs.pop('movie')
        people = self.validated_data.pop('people')

        MoviePeopleRoles.objects.filter(movie=movie).delete()
        for person_role in people:
            MoviePeopleRoles.objects.create(movie=movie, person_role=person_role)

        return movie


class WriteMovieSerializer(serializers.ModelSerializer):
    title = serializers.CharField(error_messages={'invalid': 'Invalid Title'}, write_only=True, required=True)
    release_year = serializers.DateField(write_only=True, required=True)
    people = serializers.ListField(write_only=True, required=False, child=serializers.IntegerField())

    class Meta:
        model = Movie
        fields = ('title', 'release_year', 'people',)

    def create(self, validated_data):
        people = validated_data.pop('people') if validated_data.get('people', None) else None
        instance = Movie.objects.create(**validated_data)

        if people is not None:
            serializer = WritePeopleSerializer(data={'people': people})
            serializer.is_valid(raise_exception=True)
            serializer.save(movie=instance)

        return instance

    def update(self, instance, validated_data):
        instance.title = validated_data.pop('title')
        instance.release_year = validated_data.pop('release_year')
        instance.save()

        people = validated_data.pop('people') if validated_data.get('people', None) else None
        if people is not None:
            serializer = WritePeopleSerializer(data={'people': people})
            serializer.is_valid(raise_exception=True)
            serializer.save(movie=instance)

        return instance


class WriteRolesSerializer(serializers.Serializer):
    roles = serializers.ListField(write_only=True, required=True, min_length=1,
                                  child=serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), write_only=True,
                                                                           required=True))

    def validate(self, attrs):
        data = super(WriteRolesSerializer, self).validate(attrs)
        roles = data['roles']

        if not isinstance(roles, list):
            raise serializers.ValidationError({'roles': ['Invalid Roles']})

        return data

    def save(self, **kwargs):
        person = kwargs.pop('person')
        roles = self.validated_data.pop('roles')

        PersonRoles.objects.filter(person=person).delete()
        for role in roles:
            PersonRoles.objects.create(person=person, role=role)

        return person


class WritePersonSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(error_messages={'invalid': 'Invalid First Name'}, write_only=True, required=True)
    last_name = serializers.CharField(error_messages={'invalid': 'Invalid Last Name'}, write_only=True, required=True)

    aliases = serializers.CharField(write_only=True, required=False)
    roles = serializers.ListField(write_only=True, required=False, child=serializers.IntegerField())

    class Meta:
        model = Person
        fields = ('first_name', 'last_name', 'aliases', 'roles')

    def create(self, validated_data):
        roles = validated_data.pop('roles') if validated_data.get('roles', None) else None
        instance = Person.objects.create(**validated_data)

        if roles is not None:
            serializer = WriteRolesSerializer(data={'roles': roles})
            serializer.is_valid(raise_exception=True)
            serializer.save(person=instance)

        return instance

    def update(self, instance, validated_data):
        instance.first_name = validated_data.pop('first_name')
        instance.last_name = validated_data.pop('last_name')

        if getattr(validated_data, 'aliases', None) is not None:
            instance.aliases = validated_data.pop('aliases')

        instance.save()

        roles = validated_data.pop('roles') if validated_data.get('roles', None) else None
        if roles is not None:
            serializer = WriteRolesSerializer(data={'roles': roles})
            serializer.is_valid(raise_exception=True)
            serializer.save(person=instance)

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
