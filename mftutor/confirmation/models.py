# vim: set fileencoding=utf8:
from django.db import models

from ..tutor.models import Tutor

class Confirmation(models.Model):
    tutor = models.OneToOneField(Tutor)

    study = models.CharField(max_length=500, blank=True,
            verbose_name='Studium samt sidefag/tilvalg')
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
    internal_notes = models.CharField(max_length=500, blank=True,
            verbose_name='Notat')

    class Meta:
        ordering = ('tutor',)

    def __unicode__(self):
        return u'[TutorConfirmation '+unicode(self.tutor)+u']'
