# vim:fileencoding=utf-8:
import time
from django.utils import dateformat
from django.db import models

from ..tutor.models import TutorProfile, Rus, RusClass

class ChangeLogEntry(models.Model):
    KINDS = (
            ('import', u'Import af ruslister'),
            ('rus_profile', u'Rus: profil ændret'),
            ('rus_rusclass', u'Rus: rushold ændret'),
            ('rus_arrived', u'Rus: ankommet ændret'),
            ('rus_password', u'Rus: kodeord ændret'),
            ('note_add', u'Notat tilføjet'),
            ('note_delete', u'Notat slettet'),
            ('tutor_profile', u'Tutor: profil ændret'),
            ('tutor_rusclass', u'Tutor: rushold ændret'),
            ('tutor_password', u'Tutor: kodeord ændret'),
            )
    KIND_CHOICES = KINDS

    author = models.ForeignKey(TutorProfile, verbose_name="Forfatter")
    time = models.DateTimeField(auto_now_add=True, verbose_name="Tidspunkt")
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, verbose_name='Slags')
    payload = models.TextField(blank=True, verbose_name='Beskedparameter')
    related_pk = models.IntegerField()
    serialized_data = models.TextField(blank=True)

    def json_of(self):
        # Assume local time
        time_epoch = time.mktime(self.time.timetuple())

        return {
                'pk': self.pk,
                'author': self.author.studentnumber,
                'author_name': self.author.get_full_name(),
                'time_epoch': time_epoch,
                'time_pretty': dateformat.format(self.time, "d M y, H:i"),
                'kind': self.kind,
                'payload': self.payload,
                'related_pk': self.related_pk,
                'serialized_data': self.serialized_data,
                }

    def get_related_object(self):
        if self.kind.startswith('rus_'):
            return Rus.objects.get(pk=self.related_pk)
        elif self.kind.startswith('tutor_'):
            return Tutor.objects.get(pk=self.related_pk)
        else:
            return None

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

    author = models.ForeignKey(TutorProfile, verbose_name="Forfatter")
    time = models.DateTimeField(auto_now_add=True, verbose_name="Tidspunkt")

    deleted = models.DateTimeField(blank=True, null=True, verbose_name="Slettet")

    def json_of(self):
        note_data = {
                'kind': self.subject_kind,
                'body': self.body,
                'author': self.author.studentnumber,
                'author_name': self.author.get_full_name(),
                'time_pretty': dateformat.format(self.time, "d M y, H:i"),
                }
        if self.subject_kind == 'rus':
            note_data['subject'] = TutorProfile.objects.get(rus__pk=self.subject_pk).studentnumber
        elif self.subject_kind == 'rusclass':
            note_data['subject'] = RusClass.objects.get(pk=self.subject_pk).handle
        return note_data

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
