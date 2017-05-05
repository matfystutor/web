# vim: set fileencoding=utf8:
from __future__ import unicode_literals

from django.db import models

from ..tutor.models import Tutor

class Confirmation(models.Model):
    tutor = models.OneToOneField(Tutor)

    study = models.CharField(max_length=500, blank=True,
            verbose_name='Studium samt sidefag/tilvalg')
    tutortype = models.CharField(max_length=60, blank=True,
            verbose_name='Tutor type')
    experience = models.CharField(max_length=60, blank=True,
            verbose_name='Tidligere erfaring som holdtutor')
    resits = models.CharField(max_length=500, blank=True,
            verbose_name='Reeksamener i rusugen')
    priorities = models.CharField(max_length=60, blank=True,
            verbose_name='Ønskede studieretninger')
    firstaid = models.CharField(max_length=60, blank=True,
            verbose_name='Førstehjælpskursus')
    rusfriends = models.CharField(max_length=500, blank=True,
            verbose_name='Bekendte nye studerende')
    comment = models.CharField(max_length=500, blank=True,
            verbose_name='Kommentar')
    previous_tutor = models.CharField(max_length=500, blank=True,
            verbose_name='Har du tidligere været tutor?')
    internal_notes = models.CharField(max_length=500, blank=True,
            verbose_name='Notat')

    class Meta:
        ordering = ('tutor',)

    def __str__(self):
        return '[TutorConfirmation %s]' % self.tutor

    def __unicode__(self):
        return u'[TutorConfirmation '+unicode(self.tutor)+u']'
