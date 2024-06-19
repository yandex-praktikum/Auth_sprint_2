from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from models.movies import Genre
from services.genre import GenreService, get_genre_service
from fastapi_pagination import Page, paginate

router = APIRouter()


@router.get('/{genre_id}',
            response_model=Genre,
            description="Give information about genre by id")
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)):
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return genre


@router.get('/',
            response_model=Page[Genre],
            description="Give list of all genres")
async def all_genres(genre_service: GenreService = Depends(get_genre_service)):
    genres = await genre_service.get_all()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genres not found')
    return paginate(genres)
