# coding: utf-8
# See https://docs.djangoproject.com/en/1.4/topics/auth/
# for a discussion on user profiles and django.contrib.auth
from __future__ import unicode_literals

import re

from django.utils.encoding import python_2_unicode_compatible
from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from mftutor import settings
from mftutor.tutor.managers import TutorProfileManager, TutorManager, \
    VisibleTutorGroups, RusManager, RusClassManager
from mftutor.tutor import tutorpicture_upload_to


# User data for the project that does not vary from year to year
@python_2_unicode_compatible
class TutorProfile(models.Model):
    objects = TutorProfileManager()

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)

    name = models.CharField(
        max_length=60, verbose_name="Fulde navn")
    street = models.CharField(
        max_length=80, blank=True, verbose_name="Adresse")
    city = models.CharField(
        max_length=40, blank=True, verbose_name="Postnr. og by")
    phone = models.CharField(
        max_length=20, blank=True, verbose_name="Telefonnr.")
    email = models.EmailField(
        max_length=75, verbose_name="E-mailadresse")

    study = models.CharField(
        max_length=60, blank=True, verbose_name="Studieretning")
    studentnumber = models.CharField(
        max_length=20, unique=True, blank=True, null=True,
        verbose_name="Årskortnummer")

    picture = models.ImageField(
        upload_to=tutorpicture_upload_to,
        blank=True,
    )

    def __str__(self):
        try:
            u = self.user
        except User.DoesNotExist:
            u = None
        return '%s %s %s' % (
            self.studentnumber,
            self.get_full_name(),
            u.username if u else '(no user)',
        )

    def set_default_email(self):
        if self.email == '':
            if re.match(r'[A-Z]{2}[0-9]{5}$', self.studentnumber):
                domain = settings.DEFAULT_ASB_EMAIL_DOMAIN
            else:
                domain = settings.DEFAULT_EMAIL_DOMAIN
            self.email = '%s@%s' % (self.studentnumber, domain)

    class Meta:
        verbose_name = 'tutorprofil'
        verbose_name_plural = verbose_name + 'er'

    def get_full_name(self):
        return self.name

    def get_or_create_user(self):
        u = self.user
        if u is not None:
            return u
        sn = self.studentnumber
        if sn is None:
            raise IntegrityError(
                'TutorProfile.get_or_create_user: No studentnumber')
        u = User(
            username=self.studentnumber,
            email=self.email)
        self.set_user_name(u)
        u.save()
        self.user = u
        self.save()

    @classmethod
    def set_instance_user_name(cls, tp, user=None):
        if user is None:
            user = tp.user
            if user is None:
                raise ValueError(
                    "set_instance_user_name: TutorProfile has no user")
        try:
            first_name, last_name = tp.name.split(' ', 1)
        except ValueError:
            first_name, last_name = tp.name, ''
        user.first_name = first_name
        user.last_name = last_name

    def set_user_name(self, user=None):
        self.set_instance_user_name(self, user)

    def clean(self):
        pattern = r'\+?[0-9 ]+$'
        if not re.match(pattern, self.phone):
            raise ValidationError('Telefonnummer må kun indeholde tal')
        self.phone = self.phone.replace(' ', '')


# "Arbejdsgruppe"
@python_2_unicode_compatible
class TutorGroup(models.Model):
    objects = models.Manager()
    visible_groups = VisibleTutorGroups()

    handle = models.CharField(
        max_length=20, verbose_name="Kort navn",
        help_text="Bruges i gruppens emailadresse")
    name = models.CharField(
        max_length=40, verbose_name="Langt navn",
        help_text="Vises på hjemmesiden")
    visible = models.BooleanField(default=False)
    year = models.IntegerField(verbose_name="Tutorår", null=True)
    leader = models.ForeignKey('Tutor', verbose_name='Gruppeansvarlig', null=True)

    def __str__(self):
        return '%s %s' % (self.handle, self.year)

    class Meta:
        ordering = ['-year', 'name', 'handle']
        verbose_name = 'arbejdsgruppe'
        verbose_name_plural = verbose_name + 'r'


# "Rushold"
@python_2_unicode_compatible
class RusClass(models.Model):
    objects = RusClassManager()

    id = models.AutoField(primary_key=True)
    official_name = models.CharField(
        max_length=20, verbose_name="AU-navn",
        help_text=u"DA1, MØ3, osv.")
    internal_name = models.CharField(
        max_length=20, verbose_name="Internt navn",
        help_text=u"Dat1, Møk3, osv.")
    handle = models.CharField(
        max_length=20, verbose_name="Email",
        help_text=u"dat1, mok3, osv. Bruges i holdets emailadresse")
    year = models.IntegerField(verbose_name="Tutorår")

    def get_study(self):
        for official_name, handle, internal_name in settings.RUSCLASS_BASE:
            if self.handle.startswith(handle):
                return internal_name

    def get_tutors(self):
        return Tutor.objects.filter(rusclass=self)

    def get_russes(self):
        return Rus.objects.filter(rusclass=self)

    def __str__(self):
        return self.internal_name

    class Meta:
        verbose_name = 'rushold'
        verbose_name_plural = verbose_name

        ordering = ['year', 'internal_name']


# Membership of a user for a single year
@python_2_unicode_compatible
class Tutor(models.Model):
    objects = TutorManager()

    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(TutorProfile)
    year = models.IntegerField(verbose_name="Tutorår")
    groups = models.ManyToManyField(
        TutorGroup, verbose_name="Arbejdsgrupper", blank=True)
    early_termination = models.DateTimeField(
        null=True, blank=True, verbose_name="Ekskluderet",
        help_text="Tidspunkt i året hvor tutoren stopper i foreningen")
    early_termination_reason = models.TextField(
        null=True, blank=True, verbose_name="Eksklusionsårsag",
        help_text="Årsag til at tutoren stopper")
    rusclass = models.ForeignKey(RusClass, null=True, blank=True)

    @classmethod
    def members(cls, year=None):
        if year is None:
            year = settings.YEAR

        return cls.objects.filter(
            year=year,
            early_termination__isnull=True)

    @classmethod
    def group_members(cls, handle, year=None):
        if isinstance(handle, TutorGroup):
            return cls.members(handle.year).filter(groups=handle)
        else:
            return cls.members(year).filter(groups__handle__exact=handle)

    def has_rusclass(self, year=None):
        if year is None:
            year = settings.YEAR

        return self.is_tutorbur() or self.rusclass

    def is_member(self, year=None):
        if year is None:
            year = settings.YEAR

        if self.year != year:
            return False
        elif self.early_termination is not None:
            return False
        else:
            return True
    is_member.boolean = True

    def is_tutorbest(self, year=None):
        if not self.is_member(year=year):
            return False
        elif self.groups.filter(handle__exact='best').exists():
            return True
        else:
            return False
    is_tutorbest.boolean = True

    def is_tutorbur(self):
        if not self.is_member():
            return False
        elif self.is_tutorbest():
            return True
        elif self.groups.filter(handle__exact='buret').exists():
            return True
        else:
            return False
    is_tutorbur.boolean = True

    def can_manage_rusclass(self, rusclass):
        return (self.is_tutorbest() or
                self.is_tutorbur() or
                self.rusclass == rusclass)

    def __str__(self):
        try:
            p = self.profile
        except:
            p = None
        return '%s (%s)' % (p, self.year)

    class Meta:
        ordering = ['-year']
        verbose_name = 'tutor'
        verbose_name_plural = verbose_name + 'er'
        unique_together = (('profile', 'year'),)


class TutorInTutorGroup(models.Model):
    tutorgroup = models.ForeignKey(TutorGroup, to_field='id')
    tutor = models.ForeignKey(Tutor)


@python_2_unicode_compatible
class BoardMember(models.Model):
    id = models.AutoField(primary_key=True)
    tutor = models.ForeignKey(Tutor)
    position = models.IntegerField(verbose_name="Rækkefølge")
    title = models.CharField(max_length=50, verbose_name="Titel")

    def __str__(self):
        return "%s %s" % (self.title, self.tutor)

    class Meta:
        ordering = ['tutor__year', 'position']
        verbose_name = 'bestyrelsesmedlem'
        verbose_name_plural = verbose_name + 'mer'


# Freshman semester of a user for a single year
class Rus(models.Model):
    objects = RusManager()

    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(TutorProfile)
    year = models.IntegerField(verbose_name="Tutorår")
    rusclass = models.ForeignKey(RusClass, null=True)

    arrived = models.BooleanField(verbose_name="Ankommet", default=False)
    initial_rusclass = models.ForeignKey(
        RusClass, null=True, related_name='initial_rus_set')

    class Meta:
        verbose_name = 'rus'
        verbose_name_plural = verbose_name + 'ser'

        ordering = ['rusclass', 'profile']

    def json_of(self):
        if self.initial_rusclass:
            initial_handle = self.initial_rusclass.handle
        else:
            initial_handle = None
        return {
            'year': self.year,
            'rusclass': self.rusclass.handle,
            'arrived': self.arrived,
            'pk': self.profile.pk,
            'studentnumber': self.profile.studentnumber,
            'name': self.profile.get_full_name(),
            'street': self.profile.street,
            'city': self.profile.city,
            'phone': self.profile.phone,
            'email': self.profile.email,

            'initial_rusclass': initial_handle,
        }
