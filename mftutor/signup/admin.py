from mftutor.signup.models import TutorApplication, TutorApplicationGroup
from django.contrib import admin

admin.site.register(TutorApplication, admin.ModelAdmin)
admin.site.register(TutorApplicationGroup, admin.ModelAdmin)
