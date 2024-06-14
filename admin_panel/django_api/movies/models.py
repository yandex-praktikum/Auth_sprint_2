import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from datetime import datetime


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField("created_at", auto_now_add=True)
    updated_at = models.DateTimeField("updated_at", auto_now=True)

    class Meta:
        abstract = True

class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField("name", max_length=255)
    description = models.TextField("description", blank=True, null=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _("genre")
        verbose_name_plural = _("genres")

    def __str__(self):
        return self.name 

class FilmworkType(models.TextChoices):
    MOVIE =  "movie", _("MOVIE")
    TV_SHOW = "tv_show", _("TV_SHOW")

class Filmwork(UUIDMixin, TimeStampedMixin):
    title = models.CharField(_("title"), max_length=255)
    description = models.TextField("description", blank=True, null=True)
    creation_date = models.DateField("creation_date", blank=True, null=True)
    file_path = models.TextField("file_path", blank=True, null=True)
    rating = models.FloatField("rating", blank=True, null=True,
                               validators=[MinValueValidator(0), MaxValueValidator(100)])
    # type = models.CharField("type", max_length=255, 
    #                         choices=FilmworkType.choices,
    #                         default=FilmworkType.TV)
    type = models.TextField("type", max_length=255)

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _("movie")
        verbose_name_plural = _("movies")
        indexes = [
            models.Index(fields=["creation_date"], name="creation_date_idx"),
            models.Index(fields=["rating"], name="rating_idx"),
        ]
        

    def __str__(self):
        return self.title

class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    created_at = models.DateTimeField("created_at", auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work" 

class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField("full_name", max_length=255)
    
    class Meta:
        db_table = "content\".\"person"
        verbose_name = _("role")
        verbose_name_plural = _("roles")
        indexes = [
            models.Index(fields=["full_name"], name="full_name_idx"),
        ]

    def __str__(self):
        return self.full_name 

class PersonFilmworkType(models.TextChoices):
    ACTOR =  "actor", _("Actor")
    DIRECTOR = "director", _("Director")
    WRITER = "writer", _("Writer")


class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    created_at = models.DateTimeField("created_at", auto_now_add=True)
    role = models.CharField("role", 
                            max_length=255, 
                            choices=PersonFilmworkType.choices,
                            default=PersonFilmworkType.ACTOR)

    class Meta:
        db_table = "content\".\"person_film_work" 