# vim:set fileencoding=utf-8:
from django.db import models
from ..tutor.models import Tutor
from datetime import date, datetime

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    rsvp = models.DateTimeField(blank=True, null=True, verbose_name="Tilmeldingsfrist")

    def category(self):
        if u'stormøde' in self.title:
            return 'stormoede'
        if u'RKFL' in self.title:
            return 'rkfl'
        if u'RKFW' in self.title:
            return 'rkfw'
        if u'fest' in self.title:
            return 'fest'

    @property
    def is_completed(self):
        return self.end_date < date.today()

    @property
    def is_rsvp_possible(self):
        return self.rsvp is not None and not self.rsvp < datetime.now(self.rsvp.tzinfo)

    def __str__(self):
        return '[Event %s on %s]' % (self.title, self.start_date)

    def __unicode__(self):
        return '[Event '+self.title+' on '+str(self.start_date)+']'

    class Meta:
        ordering = ['start_date', 'start_time']
        verbose_name = 'begivenhed'
        verbose_name_plural = verbose_name + 'er'

class EventParticipant(models.Model):
    event = models.ForeignKey(Event, related_name="participants")
    tutor = models.ForeignKey(Tutor, related_name="events")
    status = models.CharField(
        verbose_name='Tilbagemelding', max_length=10,
        choices=(('yes', 'Kommer'), ('no', 'Kommer ikke')))
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return '[RSVP %s %s %s]' % (self.event_id, self.tutor_id, self.status)

    def __unicode__(self):
        return '[RSVP '+str(self.event_id)+' '+str(self.tutor_id)+' '+self.status+']'

    class Meta:
        unique_together = (('event', 'tutor',),)
        verbose_name = 'tilbagemelding'
        verbose_name_plural = verbose_name + 'er'
        ordering = ['event', 'status']
