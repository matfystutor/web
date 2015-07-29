# vim: set fileencoding=utf8 :
from .models import ImportSession, ImportLine, Handout, HandoutClassResponse, HandoutRusResponse, ChangeLogEntry
from django.contrib import admin

class ImportSessionAdmin(admin.ModelAdmin):
    list_display = ('year', 'name', 'regex', 'author', 'created', 'updated')
    list_display_links = ('name',)
    list_filter = ('year',)
    search_fields = ['name']

class ImportLineAdmin(admin.ModelAdmin):
    list_display = ('session', 'position', 'line', 'matched', 'rus')
    list_display_links = ('line',)
    search_fields = ['line']

class ChangeLogEntryAdmin(admin.ModelAdmin):
    list_display = ('author', 'time', 'kind')

class HandoutAdmin(admin.ModelAdmin):
    list_filter = ('year',)

admin.site.register(ImportSession, ImportSessionAdmin)
admin.site.register(ImportLine, ImportLineAdmin)
admin.site.register(Handout, HandoutAdmin)
admin.site.register(HandoutClassResponse, admin.ModelAdmin)
admin.site.register(HandoutRusResponse, admin.ModelAdmin)
admin.site.register(ChangeLogEntry, ChangeLogEntryAdmin)
