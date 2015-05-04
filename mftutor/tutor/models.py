# coding: utf-8
# See https://docs.djangoproject.com/en/1.4/topics/auth/
# for a discussion on user profiles and django.contrib.auth
from __future__ import unicode_literals

import re
from django.db import models
from django.contrib.auth.models import User
from mftutor import settings
from mftutor.tutor.managers import TutorProfileManager, TutorManager, \
    TutorMembers, VisibleTutorGroups, RusManager


def tutorpicture_upload_to(instance, filename):
    extension = re.sub(r'^.*\.', '', filename)
    return 'tutorpics/%s.%s' % (instance.studentnumber, extension)


# User data for the project that does not vary from year to year
class TutorProfile(models.Model):
    objects = TutorProfileManager()

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User)

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
        max_length=20, verbose_name="Årskortnummer", unique=True)

    picture = models.ImageField(
        upload_to=tutorpicture_upload_to,
        blank=True,
    )

    def __str__(self):
        return '%s %s %s' % (
            self.studentnumber,
            self.get_full_name(),
            self.user.username if self.user else '(no user)',
        )

    def __unicode__(self):
        return '%s %s %s' % (
            self.studentnumber,
            self.get_full_name(),
            self.user.username if self.user else '(no user)',
        )

    def set_default_email(self):
        if self.email == '':
            if re.match(r'[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9]$', self.studentnumber):
                self.email = self.studentnumber + '@' + settings.DEFAULT_ASB_EMAIL_DOMAIN
            else:
                self.email = self.studentnumber + '@' + settings.DEFAULT_EMAIL_DOMAIN

    class Meta:
        verbose_name = 'tutorprofil'
        verbose_name_plural = verbose_name + 'er'

    def get_full_name(self):
        return self.name

# "Arbejdsgruppe"
class TutorGroup(models.Model):
    objects = models.Manager()
    visible_groups = VisibleTutorGroups()

    handle = models.CharField(max_length=20, primary_key=True, verbose_name="Kort navn",
        help_text="Bruges i gruppens emailadresse")
    name = models.CharField(max_length=40, verbose_name="Langt navn",
        help_text="Vises på hjemmesiden")
    visible = models.BooleanField(default=False)

    def __str__(self):
        return self.handle

    def __unicode__(self):
        return self.handle

    class Meta:
        ordering = ['name', 'handle']
        verbose_name = 'arbejdsgruppe'
        verbose_name_plural = verbose_name + 'r'

class RusClassManager(models.Manager):
    def create_from_official(self, year, official_name):
        translate_to_handle = {}
        for official, handle, internal in settings.RUSCLASS_BASE:
            translate_to_handle[official] = handle
        translate_to_internal = {}
        for official, handle, internal in settings.RUSCLASS_BASE:
            translate_to_internal[official] = internal
        handle = translate_to_handle[official_name[0:2]] + official_name[2:]
        internal_name = translate_to_internal[official_name[0:2]] + u' ' + official_name[2:]
        return self.model(year=year, official_name=official_name,
                handle=handle, internal_name=internal_name)

# "Rushold"
class RusClass(models.Model):
    objects = RusClassManager()

    id = models.AutoField(primary_key=True)
    official_name = models.CharField(max_length=20, verbose_name="AU-navn",
            help_text=u"DA1, MØ3, osv.")
    internal_name = models.CharField(max_length=20, verbose_name="Internt navn",
            help_text=u"Dat1, Møk3, osv.")
    handle = models.CharField(max_length=20, verbose_name="Email",
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

    def __unicode__(self):
        return self.internal_name

    class Meta:
        verbose_name = 'rushold'
        verbose_name_plural = verbose_name

        ordering = ['year', 'internal_name']

# Membership of a user for a single year
class Tutor(models.Model):
    objects = TutorManager()
    members = TutorMembers()

    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(TutorProfile)
    year = models.IntegerField(verbose_name="Tutorår")
    groups = models.ManyToManyField(TutorGroup, verbose_name="Arbejdsgrupper", blank=True)
    early_termination = models.DateTimeField(null=True, blank=True, verbose_name="Ekskluderet",
        help_text="Tidspunkt i året hvor tutoren stopper i foreningen")
    early_termination_reason = models.TextField(null=True, blank=True, verbose_name="Eksklusionsårsag",
        help_text="Årsag til at tutoren stopper")
    rusclass = models.ForeignKey(RusClass, null=True, blank=True)

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
        return (self.is_tutorbest()
                or self.is_tutorbur()
                or self.rusclass == rusclass)

    def __str__(self):
        return '%s (%s)' % (self.profile, self.year)

    def __unicode__(self):
        return '%s (%s)' % (self.profile, self.year)

    class Meta:
        ordering = ['-year']
        verbose_name = 'tutor'
        verbose_name_plural = verbose_name + 'er'
        unique_together = (('profile', 'year'),)

class TutorGroupLeader(models.Model):
    group = models.ForeignKey(TutorGroup)
    year = models.IntegerField()
    tutor = models.ForeignKey(Tutor)

    class Meta:
        ordering = ['-year', 'group']
        verbose_name = 'gruppeansvarlig'
        verbose_name_plural = verbose_name + 'e'
        unique_together = (('group', 'year'),)

def tutor_group_leader(group, year):
    try:
        leader_object = TutorGroupLeader.objects.get(group=group, year=year)
        return leader_object.tutor
    except TutorGroupLeader.DoesNotExist:
        return None

class BoardMember(models.Model):
    id = models.AutoField(primary_key=True)
    tutor = models.ForeignKey(Tutor)
    position = models.IntegerField(verbose_name="Rækkefølge")
    title = models.CharField(max_length=50, verbose_name="Titel")

    def __str__(self):
        return "%s %s" % (self.title, self.tutor)

    def __unicode__(self):
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
    initial_rusclass = models.ForeignKey(RusClass, null=True, related_name='initial_rus_set')

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
                'studentnumber': self.profile.studentnumber,
                'name': self.profile.get_full_name(),
                'street': self.profile.street,
                'city': self.profile.city,
                'phone': self.profile.phone,
                'email': self.profile.email,

                'initial_rusclass': initial_handle,
                }
