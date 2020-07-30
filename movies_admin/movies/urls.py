from rest_framework import routers

from .views import (
    PersonViewSet,
    MovieViewSet,
)

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'people', PersonViewSet, basename='people')
router.register(r'movies', MovieViewSet, basename='movies')
urlpatterns = router.urls

