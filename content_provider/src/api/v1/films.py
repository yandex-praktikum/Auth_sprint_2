from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.film import FilmService, get_film_service, Pagination

from models.movies import Film
from typing import List

router = APIRouter()



@router.get(
        '/search',
        summary="Find film by title",
        response_model=List[Film])
async def search_film(phrase: str,
                      pagination: Pagination = Depends(),
                      film_service: FilmService = Depends(get_film_service)
    ):
    """
    Find films by a phrase in the title:

    - **phrase**: must be in the title
    - **pagination**: number of the page shown and number of items on the page
    """
    films = await film_service.get_by_search(phrase, pagination.page, pagination.size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return films

@router.get(
        '/{film_id}',
        summary="Find films by ID",
        response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    """
    Find a film by ID

    - ***film_id**: internal identificator of the film
    """
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return film


@router.get(
        '/', 
        summary="Find films by genre, title, sort by any field",
        response_model=List[Film]
        )
async def film_details(
        sort: str = Query(None),
        genre: str = Query(None),
        query: str = Query(None),
        pagination: Pagination = Depends(),
        film_service: FilmService = Depends(get_film_service)
    ):
    """
    Find films by a genre, a phrase in the title, sort by any field:
    - **sort**: a field in the Film model by which to sort
    - **genre**: a genre of the film 
    - **query**: a phrase which must be in the title
    - **pagination**: number of the page shown and number of items on the page
    """
    films = await film_service.get(genre=genre, title=query, page=pagination.page, size=pagination.size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    if sort:
        reverse_sort = False
        if sort.startswith('-'):
            reverse_sort = True
            sort = sort[1:]  # Убираем знак минуса
        films = sorted(films, key=lambda x: getattr(x, sort), reverse=reverse_sort)
    return films




