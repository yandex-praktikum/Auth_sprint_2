from fastapi.routing import APIRouter

from api.v1 import films, persons, genres, health


router = APIRouter()
router.include_router(films.router, prefix='/films', tags=['films'])
router.include_router(persons.router, prefix='/persons', tags=['persons'])
router.include_router(genres.router, prefix='/genres', tags=['genres'])
router.include_router(health.router, prefix='/health', tags=['health'])
