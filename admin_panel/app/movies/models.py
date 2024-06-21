import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_("name"), max_length=255, unique=True)
    description = models.TextField(_("description"), blank=True)

    class Meta:
        db_table = 'content"."genre'
        indexes = [models.Index(fields=("name",))]
        verbose_name = _("genre")
        verbose_name_plural = _("genres")

    def __str__(self):
        return self.name


class GenreFilmWork(UUIDMixin):
    genre = models.ForeignKey("Genre", verbose_name=_("genre"), on_delete=models.CASCADE)
    film_work = models.ForeignKey("FilmWork", verbose_name=_("film_work"), on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("created"), null=True)

    class Meta:
        db_table = 'content"."genre_film_work'
        constraints = [models.UniqueConstraint(fields=("genre", "film_work"), name="unique_genre_film_work")]
        verbose_name = _("film genre")
        verbose_name_plural = _("film genres")


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_("full_name"), max_length=255)

    class Meta:
        db_table = 'content"."person'
        indexes = [models.Index(fields=("full_name",))]
        verbose_name = _("person")
        verbose_name_plural = _("persons")

    def __str__(self):
        return self.full_name


class PersonFilmWork(UUIDMixin):
    class Roles(models.TextChoices):
        ACTOR = "actor", _("actor")
        DIRECTOR = "director", _("director")
        PRODUCER = "producer", _("producer")
        WRITER = "writer", _("writer")

    person = models.ForeignKey("Person", verbose_name=_("person"), on_delete=models.CASCADE)
    film_work = models.ForeignKey("FilmWork", verbose_name=_("film_work"), on_delete=models.CASCADE)
    role = models.CharField(choices=Roles.choices, verbose_name=_("role"))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("created"), null=True)

    class Meta:
        db_table = 'content"."person_film_work'
        constraints = [
            models.UniqueConstraint(fields=("person", "film_work", "role"), name="unique_person_film_work_role")
        ]
        verbose_name = _("film participant")
        verbose_name_plural = _("film participants")


class FilmWork(UUIDMixin, TimeStampedMixin):
    class FilmWorkType(models.TextChoices):
        MOVIE = "movie", _("movie")
        TV_SHOW = "tv_show", _("tv show")

    title = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    creation_date = models.DateField(_("creation_date"), null=True)
    rating = models.FloatField(
        _("rating"), blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    type = models.CharField(_("type"), choices=FilmWorkType.choices)

    genres = models.ManyToManyField(Genre, through="GenreFilmWork")
    persons = models.ManyToManyField(Person, through="PersonFilmWork")

    class Meta:
        db_table = 'content"."film_work'
        indexes = [models.Index(fields=("creation_date", "rating"))]
        verbose_name = _("film work")
        verbose_name_plural = _("film works")

    def __str__(self):
        return self.title
