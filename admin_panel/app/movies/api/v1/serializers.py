from rest_framework import serializers

from movies.models import FilmWork


class FilmWorkSerializer(serializers.ModelSerializer):
    genres = serializers.ListField(child=serializers.CharField())
    directors = serializers.ListField(child=serializers.CharField())
    writers = serializers.ListField(child=serializers.CharField())
    actors = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = FilmWork
        exclude = ["persons"]
