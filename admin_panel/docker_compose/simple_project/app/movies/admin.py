from django.contrib import admin
from .models import Genre, Person, Filmwork, GenreFilmwork, PersonFilmwork


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork
    autocomplete_fields = ['person']
    

@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, PersonFilmworkInline)
    list_display = ('title', 'type', 'creation_date', 'rating') 
    list_filter = ('type',) 
    search_fields = ('title', 'description', 'id') 


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    ...

    
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ["full_name"]
