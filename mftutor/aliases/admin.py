from .models import Alias
from django.contrib import admin

class AliasAdmin(admin.ModelAdmin):
    list_display = ('source', 'destination')
    search_fields = ('source', 'destination')

admin.site.register(Alias, AliasAdmin)
