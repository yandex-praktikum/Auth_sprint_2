from rest_framework import routers

from .views import FilmWorkReadOnlyViewSet

router = routers.DefaultRouter()
router.register("movies", FilmWorkReadOnlyViewSet, basename="FilmWork")

urlpatterns = router.urls
