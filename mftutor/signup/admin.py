from mftutor.signup.models import (
    TutorApplication, TutorApplicationGroup,
    EmailTemplate)
from django.contrib import admin


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('year', 'name', 'subject')
    list_filter = ('year',)


class TutorApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'study', 'year')
    list_filter = ('year',)


class TutorApplicationGroupAdmin(admin.ModelAdmin):
    list_display = ('group_name', 'application_name')

    def application_name(self, obj):
        return obj.application.name

    def group_name(self, obj):
        return obj.group.name


admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(TutorApplication, TutorApplicationAdmin)
admin.site.register(TutorApplicationGroup, TutorApplicationGroupAdmin)
