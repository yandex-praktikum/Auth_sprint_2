from django.contrib import admin
from django.contrib.auth.models import Group as DjangoGroup

admin.site.unregister(DjangoGroup)
