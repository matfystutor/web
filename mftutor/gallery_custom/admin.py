from django import forms
from django.contrib import admin

from photologue.admin import PhotoAdmin as PhotoAdminDefault
from photologue.models import Watermark, PhotoEffect, Photo

admin.site.unregister(Watermark)
admin.site.unregister(PhotoEffect)



class PhotoAdminForm(forms.ModelForm):
    """ #NoFilter """

    class Meta:
        model = Photo
        exclude = [ 'effect',
                    'sites',
                  ]


class PhotoAdmin(PhotoAdminDefault):
    form = PhotoAdminForm

admin.site.unregister(Photo)
admin.site.register(Photo, PhotoAdmin)
