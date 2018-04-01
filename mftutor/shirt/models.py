# vim: set fileencoding=utf8:
from django.core.exceptions import ValidationError
from django.db import models

from ..tutor.models import TutorProfile

class ShirtPreference(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(TutorProfile)
    choice1 = models.CharField(max_length=60)
    choice2 = models.CharField(max_length=60)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def is_valid_option(self, value):
        return ShirtOption.objects.filter(choice__exact=value).count() != 0

    def clean(self):
        if not self.is_valid_option(self.choice1) or not self.is_valid_option(self.choice2):
            raise ValidationError('Ugyldig størrelse')

class ShirtOption(models.Model):
    id = models.AutoField(primary_key=True)
    choice = models.CharField(max_length=60)
    position = models.IntegerField()

    class Meta:
        ordering = ('position',)

    def __str__(self):
        return self.choice

    def __unicode__(self):
        return self.choice
