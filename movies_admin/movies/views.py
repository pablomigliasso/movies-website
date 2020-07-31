from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
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


class PersonViewSet(viewsets.ModelViewSet,):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

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


class MovieViewSet(viewsets.ModelViewSet,):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

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
