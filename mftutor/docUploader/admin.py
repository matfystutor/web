# vim: set fileencoding=utf8 :
from .models import Document
from django.contrib import admin

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('type', 'year', 'title', 'doc_file','time_of_upload')
    list_display_links = ('title',)
	

admin.site.register(Document, DocumentAdmin)
