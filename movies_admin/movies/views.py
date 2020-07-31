from rest_framework import status, viewsets

from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
)
from rest_framework.response import Response

from .models import (
    Movie,
    Person,
)

from .serializers import (
    MovieSerializer,
    PersonSerializer,
    WritePersonSerializer,
    WriteMovieSerializer,
)


class PersonViewSet(viewsets.GenericViewSet, ListModelMixin, RetrieveModelMixin, DestroyModelMixin,):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

    def partial_update(self, request, *args, **kwargs):
        person = self.get_object()

        serializer = WritePersonSerializer(instance=person, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        serializer = PersonSerializer(instance=instance)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = WritePersonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()
        serializer = PersonSerializer(instance=instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MovieViewSet(viewsets.GenericViewSet, ListModelMixin, RetrieveModelMixin, DestroyModelMixin,):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    def partial_update(self, request, *args, **kwargs):
        movie = self.get_object()

        serializer = WriteMovieSerializer(instance=movie, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        serializer = MovieSerializer(instance=instance)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = WriteMovieSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()
        serializer = MovieSerializer(instance=instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
