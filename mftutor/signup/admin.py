from mftutor.signup.models import (
    TutorApplication, TutorApplicationGroup,
    EmailTemplate)
from django.contrib import admin


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('year', 'name', 'subject')
    list_filter = ('year',)


admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(TutorApplication, admin.ModelAdmin)
admin.site.register(TutorApplicationGroup, admin.ModelAdmin)
