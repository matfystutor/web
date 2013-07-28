# vim:fileencoding=utf-8:
from django.db import models

from ..tutor.models import TutorProfile, Rus, RusClass

class ChangeLogEntry(models.Model):
    author = models.ForeignKey(TutorProfile, verbose_name="Forfatter")
    time = models.DateTimeField(auto_now_add=True, verbose_name="Tidspunkt")
    deleted = models.DateTimeField(blank=True, null=True, verbose_name="Slettet")
    hidden = models.DateTimeField(blank=True, null=True, verbose_name="Skjult")
    short_message = models.CharField(blank=True, max_length=500, verbose_name="Kort besked")
    message = models.CharField(max_length=500, verbose_name="Besked")
    can_rollback = models.BooleanField(verbose_name="Kan fortrydes")
    can_delete = models.BooleanField(verbose_name="Kan slettes")

class ChangeLogEffect(models.Model):
    entry = models.ForeignKey(ChangeLogEntry)

    model = models.CharField(max_length=10, choices=[(a,a) for a in ('user', 'profile', 'rusclass', 'rus')])
    pk = models.IntegerField()
    what = models.CharField(max_length=10, choices=[(a,a) for a in ('created', 'modified', 'deleted')])
    field = models.CharField(blank=True, max_length=50)
    old_value = models.CharField(blank=True, max_length=500)
    new_value = models.CharField(blank=True, max_length=500)

class ImportSession(models.Model):
    year = models.IntegerField(verbose_name="Tutorår")
    name = models.CharField(max_length=200, verbose_name="Navn")
    regex = models.CharField(max_length=500, verbose_name="Regulært udtryk")
    author = models.ForeignKey(TutorProfile, verbose_name="Forfatter")

    created = models.DateTimeField(auto_now_add=True, verbose_name="Oprettet")
    updated = models.DateTimeField(auto_now=True, verbose_name="Sidst ændret")
    imported = models.DateTimeField(null=True, blank=True, verbose_name="Importeret")

class ImportLine(models.Model):
    session = models.ForeignKey(ImportSession)
    line = models.CharField(max_length=500)
    position = models.IntegerField()

    matched = models.BooleanField()
    rusclass = models.CharField(max_length=500, blank=True)
    studentnumber = models.CharField(max_length=500, blank=True)
    name = models.CharField(max_length=500, blank=True)

    rus = models.ForeignKey(Rus, null=True, blank=True, on_delete=models.SET_NULL)

    def clean(self):
        from django.core.exceptions import ValidationError

        errors = {}
        if self.matched:
            for nonblank in ('rusclass', 'studentnumber', 'name'):
                if self[nonblank] == '':
                    errors[nonblank] = u'Dette felt må ikke være tomt når matched=True.'

        if errors:
            raise ValidationError(errors)

class Note(models.Model):
    subject_kind = models.CharField(max_length=10, choices=[(a,a) for a in ('rus', 'rusclass', 'tutor')])
    subject_pk = models.IntegerField()
    body = models.TextField(verbose_name='Note')

    previous = models.ForeignKey('self', blank=True, null=True)
    author = models.ForeignKey(TutorProfile, verbose_name="Forfatter")
    time = models.DateTimeField(auto_now_add=True, verbose_name="Tidspunkt")

    deleted = models.DateTimeField(blank=True, null=True, verbose_name="Slettet")
    superseded = models.DateTimeField(blank=True, null=True, verbose_name="Skjult")

class Handout(models.Model):
    KINDS = (
        ('note', u'Enkelt bemærkning'),
        ('subset', u'Tilmelding'),
    )

    PRESETS = (
        (u'Holdets time', 'note'),
        (u'Holdrepræsentant', 'note'),
        (u'Hytteansvarlig', 'note'),
        (u'Spis en rus-adresse', 'note'),
        (u'TK-intro tid', 'note'),
        (u'TØ-instruktor', 'note'),
        (u'Læsegrupper', 'subset'),
        (u'Rushyg', 'subset'),
        (u'Rustur', 'subset'),
        (u'Sportsdag', 'subset'),
        (u'Sportsdagshold', 'subset'),
        (u'Studenterhus', 'subset'),
    )

    year = models.IntegerField(verbose_name="Tutorår")
    kind = models.CharField(blank=False, max_length=10, choices=KINDS,
            verbose_name='Slags')
    name = models.CharField(max_length=100,
            verbose_name='Navn')
    note = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True, verbose_name="Oprettet")
    updated = models.DateTimeField(auto_now=True, verbose_name="Sidst ændret")

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'tilmeldingsliste'
        verbose_name_plural = verbose_name + 'r'

        unique_together = (('year', 'name'),)

class HandoutClassResponse(models.Model):
    handout = models.ForeignKey(Handout)
    rusclass = models.ForeignKey(RusClass)
    note = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True, verbose_name="Oprettet")
    updated = models.DateTimeField(auto_now=True, verbose_name="Sidst ændret")

    class Meta:
        verbose_name = 'holdbesvarelse'
        verbose_name_plural = verbose_name + 'r'
        unique_together = (('handout', 'rusclass'),)

class HandoutRusResponse(models.Model):
    handout = models.ForeignKey(Handout)
    rus = models.ForeignKey(Rus)
    checkmark = models.BooleanField()
    note = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True, verbose_name="Oprettet")
    updated = models.DateTimeField(auto_now=True, verbose_name="Sidst ændret")

    class Meta:
        verbose_name = 'rusbesvarelse'
        verbose_name_plural = verbose_name + 'r'
        unique_together = (('handout', 'rus'),)

class HandoutDeadline(models.Model):
    handout = models.ForeignKey(Handout)
    rusclass = models.ForeignKey(RusClass)
    soft_deadline = models.DateTimeField()
    hard_deadline = models.DateTimeField()
