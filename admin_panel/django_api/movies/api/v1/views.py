from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView

from movies.models import Filmwork, GenreFilmwork, PersonFilmwork


class MoviesListApi(BaseListView):
    model = Filmwork
    http_method_names = ['get']  # Список методов, которые реализует обработчик
    paginate_by = 50
    
    def get_queryset(self):
        return Filmwork.objects.all()
        
    def get_genres_by_filmwork(self, filmwork_id):
        return GenreFilmwork.objects.filter(film_work_id=filmwork_id).all()

    def get_persons_by_filmwork(self, filmwork_id, role):
        return PersonFilmwork.objects.filter(
            film_work_id=filmwork_id, role=role
        ).all()

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset, 
            self.paginate_by
        )

        page_number = self.request.GET.get("page", None)
        
        if page_number is not None:
            if page_number == 'last':
                page_number = paginator.num_pages
                prev_page = int(page_number) - 1
                next_page = None
            else:
                prev_page = int(page_number) - 1
                next_page = int(page_number) + 1
            page = paginator.page(page_number)
            return {
                'count': paginator.count,
                'total_pages': paginator.num_pages,
                'prev': prev_page,
                'next': next_page,
                'results': [
                    {
                        'id': filmwork.id,
                        'title': filmwork.title,
                        'description': filmwork.description,
                        'creation_date': filmwork.creation_date,
                        'rating': filmwork.rating,
                        'type': filmwork.type,
                        'genres': [
                            gf.genre.name for gf in self.get_genres_by_filmwork(filmwork.id)
                        ],
                        'actors': [
                            pf.person.full_name for pf in  self.get_persons_by_filmwork(filmwork.id, 'actor')
                        ],
                        'writers': [
                            pf.person.full_name for pf in  self.get_persons_by_filmwork(filmwork.id, 'writer')
                        ],
                        'directors': [
                            pf.person.full_name for pf in  self.get_persons_by_filmwork(filmwork.id, 'director')
                        ]
                    } 
                    for filmwork in page.object_list
                ]
            } 
        else:
            return {
                'count': paginator.count,
                'total_pages': paginator.num_pages,
                'prev': None,
                'next': 2,
                'results': [
                    {
                        'id': filmwork.id,
                        'title': filmwork.title,
                        'description': filmwork.description,
                        'creation_date': filmwork.creation_date,
                        'rating': filmwork.rating,
                        'type': filmwork.type,
                        'genres': [
                            gf.genre.name for gf in self.get_genres_by_filmwork(filmwork.id)
                        ],
                        'actors': [
                            pf.person.full_name for pf in  self.get_persons_by_filmwork(filmwork.id, 'actor')
                        ],
                        'writers': [
                            pf.person.full_name for pf in  self.get_persons_by_filmwork(filmwork.id, 'writer')
                        ],
                        'directors': [
                            pf.person.full_name for pf in  self.get_persons_by_filmwork(filmwork.id, 'director')
                        ]
                    } 
                    for filmwork in queryset
                ]
            }


    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        return Filmwork.objects.all()
        
    def get_genres_by_filmwork(self, filmwork_id):
        return GenreFilmwork.objects.filter(film_work_id=filmwork_id).all()

    def get_persons_by_filmwork(self, filmwork_id, role):
        return PersonFilmwork.objects.filter(
            film_work_id=filmwork_id, role=role
        ).all()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        pk = kwargs["object"].id
        filmwork = queryset.filter(id=pk)[0]

        return {            
            'id': filmwork.id,
            'title': filmwork.title,
            'description': filmwork.description,
            'creation_date': filmwork.creation_date,
            'rating': filmwork.rating,
            'type': filmwork.type,
            'genres': [
                gf.genre.name for gf in self.get_genres_by_filmwork(filmwork.id)
            ],
            'actors': [
                pf.person.full_name for pf in  self.get_persons_by_filmwork(filmwork.id, 'actor')
            ],
            'writers': [
                pf.person.full_name for pf in  self.get_persons_by_filmwork(filmwork.id, 'writer')
            ],
            'directors': [
                pf.person.full_name for pf in  self.get_persons_by_filmwork(filmwork.id, 'director')
            ]
        }
