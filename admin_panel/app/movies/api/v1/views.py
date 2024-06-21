from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from rest_framework.viewsets import ReadOnlyModelViewSet

from movies.models import FilmWork, PersonFilmWork

from .serializers import FilmWorkSerializer


class FilmWorkReadOnlyViewSet(ReadOnlyModelViewSet):
    model = FilmWork
    serializer_class = FilmWorkSerializer

    def get_queryset(self):
        genres = ArrayAgg("genres__name", distinct=True)
        directors = ArrayAgg(
            "persons__full_name", filter=Q(personfilmwork__role=PersonFilmWork.Roles.DIRECTOR), distinct=True
        )
        writers = ArrayAgg(
            "persons__full_name", filter=Q(personfilmwork__role=PersonFilmWork.Roles.WRITER), distinct=True
        )
        actors = ArrayAgg(
            "persons__full_name", filter=Q(personfilmwork__role=PersonFilmWork.Roles.ACTOR), distinct=True
        )
        return FilmWork.objects.values().annotate(genres=genres, directors=directors, writers=writers, actors=actors)
