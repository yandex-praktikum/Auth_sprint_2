import uuid
from dataclasses import dataclass, field


@dataclass
class FilmWork:
    id: uuid.UUID
    title: str
    description: str
    imdb_rating: float
    persons: list[dict]
    genres: list[str]
    actors_names: list = field(init=False)
    writers_names: list = field(init=False)
    directors_names: list = field(init=False)
    actors: list = field(init=False)
    writers: list = field(init=False)
    directors: list = field(init=False)

    def __post_init__(self):
        self.actors_names, self.actors = [], []
        self.writers_names, self.writers = [], []
        self.directors_names, self.directors = [], []
        for person in self.persons:
            if person["person_role"] == "actor":
                self.actors_names.append(person["person_name"])
                person_dict = {"id": person["person_id"], "name": person["person_name"]}
                self.actors.append(person_dict)
            elif person["person_role"] == "writer":
                self.writers_names.append(person["person_name"])
                person_dict = {"id": person["person_id"], "name": person["person_name"]}
                self.writers.append(person_dict)
            elif person["person_role"] == "director":
                self.directors_names.append(person["person_name"])
                person_dict = {"id": person["person_id"], "name": person["person_name"]}
                self.directors.append(person_dict)


@dataclass
class FilmsInPerson:
    filmwork_id: uuid.UUID
    roles: str | list
    title: str
    imdb_rating: float


@dataclass
class Person:
    id: uuid.UUID
    full_name: str
    films: list[FilmsInPerson]

    def __post_init__(self):
        unique_films = []
        for film in self.films:
            if any(x['filmwork_id'] == film['filmwork_id'] for x in unique_films):
                for unqie_film in unique_films:
                    if film['filmwork_id'] == unqie_film['filmwork_id'] and film['roles'] not in unqie_film['roles']:
                        unqie_film['roles'].append(film['roles'])
            else:
                film['roles'] = [film['roles']]
                unique_films.append(film)
        self.films = unique_films

@dataclass
class Genre:
    id: uuid.UUID
    name: str