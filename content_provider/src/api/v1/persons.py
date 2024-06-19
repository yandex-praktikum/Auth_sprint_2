from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from services.person import PersonService, get_person_service, Pagination
from fastapi_pagination import Page, paginate

router = APIRouter()


class SFilmsSearchPerson(BaseModel):
    id: UUID = Field(validation_alias='filmwork_id')
    roles: list


class SPersonSearch(BaseModel):
    uuid: UUID = Field(alias='id')
    full_name: str
    films: list[SFilmsSearchPerson]


@router.get('/search',
            response_model=list[SPersonSearch],
            response_model_by_alias=False,
            description="Search by person")
async def search_person(phrase: str,
                        pagination: Pagination = Depends(),
                        person_service: PersonService = Depends(get_person_service)):
    persons = await person_service.get_by_search(phrase, pagination.page, pagination.size)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found')
    return persons


class SFilmsPerson(BaseModel):
    id: UUID
    roles: list


class SPerson(BaseModel):
    uuid: UUID
    full_name: str
    films: list[SFilmsPerson]


@router.get('/{person_id}',
            response_model=SPerson,
            description="Give information about person by id")
async def person_details(person_id: str,
                         person_service: PersonService = Depends(get_person_service)):
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return person


class SFilmsWithPerson(BaseModel):
    id: UUID
    title: str
    imdb_rating: float


@router.get('/{person_id}/films',
            response_model=Page[SFilmsWithPerson],
            response_model_by_alias=False,
            description="Give films where person work")
async def films_list(person_id: str,
                     person_service: PersonService = Depends(get_person_service)):
    films = await person_service.films_with_person(person_id)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return paginate(films)
