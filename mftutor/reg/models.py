# vim:fileencoding=utf-8:


import time
from django.utils import dateformat
from django.db import models

from mftutor.tutor.models import Tutor, TutorProfile, Rus, RusClass


class ChangeLogEntry(models.Model):
    KINDS = (
        ('import', 'Import af ruslister'),
        ('rus_profile', 'Rus: profil ændret'),
        ('rus_rusclass', 'Rus: rushold ændret'),
        ('rus_arrived', 'Rus: ankommet ændret'),
        ('rus_password', 'Rus: kodeord ændret'),
        ('note_add', 'Notat tilføjet'),
        ('note_delete', 'Notat slettet'),
        ('tutor_profile', 'Tutor: profil ændret'),
        ('tutor_rusclass', 'Tutor: rushold ændret'),
        ('tutor_password', 'Tutor: kodeord ændret'),
    )
    KIND_CHOICES = KINDS

    author = models.ForeignKey(TutorProfile, models.CASCADE, verbose_name="Forfatter")
    time = models.DateTimeField(auto_now_add=True, verbose_name="Tidspunkt")
    kind = models.CharField(
        max_length=20, choices=KIND_CHOICES, verbose_name='Slags')
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
    author = models.ForeignKey(TutorProfile, models.CASCADE, verbose_name="Forfatter")

    created = models.DateTimeField(auto_now_add=True, verbose_name="Oprettet")
    updated = models.DateTimeField(auto_now=True, verbose_name="Sidst ændret")
    imported = models.DateTimeField(
        null=True, blank=True, verbose_name="Importeret")


class ImportLine(models.Model):
    session = models.ForeignKey(ImportSession, models.CASCADE)
    line = models.CharField(max_length=500)
    position = models.IntegerField()

    matched = models.BooleanField(default=False)
    rusclass = models.CharField(max_length=500, blank=True)
    studentnumber = models.CharField(max_length=500, blank=True)
    name = models.CharField(max_length=500, blank=True)

    rus = models.ForeignKey(
        Rus, null=True, blank=True, on_delete=models.SET_NULL)

    def clean(self):
        from django.core.exceptions import ValidationError

        errors = {}
        if self.matched:
            for nonblank in ('rusclass', 'studentnumber', 'name'):
                if self[nonblank] == '':
                    errors[nonblank] = (
                        'Dette felt må ikke være tomt når matched=True.')

        if errors:
            raise ValidationError(errors)

    class Meta:
        ordering = ['position']


class Note(models.Model):
    subject_kind = models.CharField(
        max_length=10, choices=[(a, a) for a in ('rus', 'rusclass', 'tutor')])
    subject_pk = models.IntegerField()
    body = models.TextField(verbose_name='Note')

    author = models.ForeignKey(TutorProfile, models.CASCADE, verbose_name="Forfatter")
    time = models.DateTimeField(auto_now_add=True, verbose_name="Tidspunkt")

    deleted = models.DateTimeField(
        blank=True, null=True, verbose_name="Slettet")

    def json_of(self):
        note_data = {
            'kind': self.subject_kind,
            'body': self.body,
            'author': self.author.studentnumber,
            'author_name': self.author.get_full_name(),
            'time_pretty': dateformat.format(self.time, "d M y, H:i"),
        }
        if self.subject_kind == 'rus':
            tp = TutorProfile.objects.get(rus__pk=self.subject_pk)
            note_data['subject'] = tp.pk
        elif self.subject_kind == 'rusclass':
            rc = RusClass.objects.get(pk=self.subject_pk)
            note_data['subject'] = rc.handle
        return note_data


class Handout(models.Model):
    KINDS = (
        ('note', 'Enkelt bemærkning'),
        ('subset', 'Tilmelding'),
    )

    PRESETS = (
        ('Holdets time', 'note'),
        ('Holdrepræsentant', 'note'),
        ('Hytteansvarlig', 'note'),
        ('Rustesammenaften', 'note'),
        ('TK-intro tid', 'note'),
        ('TØ-instruktor', 'note'),
        ('Læsegrupper', 'subset'),
        ('Rushyg', 'subset'),
        ('Rustur', 'subset'),
        ('Sportsdag', 'subset'),
        ('Sportsdagshold', 'subset'),
        ('Studenterhus', 'subset'),
    )

    year = models.IntegerField(verbose_name="Tutorår")
    kind = models.CharField(blank=False, max_length=10, choices=KINDS,
                            verbose_name='Slags')
    name = models.CharField(max_length=100,
                            verbose_name='Navn')
    note = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True, verbose_name="Oprettet")
    updated = models.DateTimeField(auto_now=True, verbose_name="Sidst ændret")

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'tilmeldingsliste'
        verbose_name_plural = verbose_name + 'r'

        unique_together = (('year', 'name'),)


class HandoutClassResponse(models.Model):
    COLORS = (
        ('green', 'Grøn'),
        ('yellow', 'Gul'),
        ('red', 'Rød'),
    )

    handout = models.ForeignKey(Handout, models.CASCADE)
    rusclass = models.ForeignKey(RusClass, models.CASCADE)
    color = models.CharField(max_length=10, choices=COLORS, default='green')
    note = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True, verbose_name="Oprettet")
    updated = models.DateTimeField(auto_now=True, verbose_name="Sidst ændret")

    class Meta:
        verbose_name = 'holdbesvarelse'
        verbose_name_plural = verbose_name + 'r'
        unique_together = (('handout', 'rusclass'),)


class HandoutRusResponse(models.Model):
    handout = models.ForeignKey(Handout, models.CASCADE)
    rus = models.ForeignKey(Rus, models.CASCADE)
    checkmark = models.BooleanField(default=False)
    note = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True, verbose_name="Oprettet")
    updated = models.DateTimeField(auto_now=True, verbose_name="Sidst ændret")

    class Meta:
        verbose_name = 'rusbesvarelse'
        verbose_name_plural = verbose_name + 'r'
        unique_together = (('handout', 'rus'),)


class LightboxRusClassStateManager(models.Manager):
    def get_for_year(self, year):
        rusclasses = RusClass.objects.filter(year=year)
        rusclass_handles = frozenset(
            rusclass.handle for rusclass in rusclasses)
        rusclass_dict = {}
        for rusclass in rusclasses:
            rusclass_dict[rusclass.handle] = rusclass

        states = self.model.objects.filter(rusclass__in=rusclasses)
        states = states.select_related('rusclass')
        state_handles = frozenset(state.rusclass.handle for state in states)

        missing = rusclass_handles.difference(state_handles)
        new = [self.model(rusclass=rusclass_dict[handle])
               for handle in missing]

        return list(states) + list(new)


class LightboxRusClassState(models.Model):
    objects = LightboxRusClassStateManager()

    COLORS = (
        ('green', 'Grøn'),
        ('yellow', 'Gul'),
        ('red', 'Rød'),
    )

    rusclass = models.OneToOneField(RusClass, models.CASCADE)
    color = models.CharField(max_length=10, choices=COLORS, default='green')
    note = models.TextField(blank=True)
    author = models.ForeignKey(
        TutorProfile, models.CASCADE, null=True, verbose_name="Forfatter")
    updated = models.DateTimeField(auto_now=True, verbose_name="Sidst ændret")

    class Meta:
        verbose_name = 'tavlestatus'
        verbose_name_plural = verbose_name + 'er'
        ordering = ['rusclass']


class LightboxNoteManager(models.Manager):
    def get_for_year(self, year):
        try:
            return self.model.objects.get(year=year)
        except self.model.DoesNotExist:
            return self.model(year=year)


class LightboxNote(models.Model):
    objects = LightboxNoteManager()
    COLORS = (
        ('Grøn', 'green'),
        ('Gul', 'yellow'),
        ('Rød', 'red'),
    )

    year = models.IntegerField(verbose_name="Tutorår", unique=True)
    note = models.TextField(blank=True)
    author = models.ForeignKey(
        TutorProfile, models.CASCADE, null=True, verbose_name="Forfatter")
    updated = models.DateTimeField(auto_now=True, verbose_name="Sidst ændret")
    color = models.CharField(max_length=10, choices=COLORS, default='green')
