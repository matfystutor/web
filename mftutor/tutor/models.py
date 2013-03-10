# coding: utf-8
# See https://docs.djangoproject.com/en/1.4/topics/auth/
# for a discussion on user profiles and django.contrib.auth

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from ..settings import YEAR
from .managers import TutorProfileManager, TutorManager, TutorMembers

def tutorpicture_upload_to(instance, filename):
    import re
    extension = re.sub(r'^.*\.', '', filename)
    return 'tutorpics/'+instance.studentnumber+'.'+extension

# User data for the project that does not vary from year to year
class TutorProfile(models.Model):
    objects = TutorProfileManager()

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)

    #name = models.CharField(max_length=60, verbose_name="Fulde navn")
    # first name and last name exist in User
    street = models.CharField(max_length=80, blank=True, verbose_name="Adresse")
    city = models.CharField(max_length=40, blank=True, verbose_name="Postnr. og by")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefonnr.")
    #email = models.EmailField(verbose_name="E-mailadresse")
    # Email address exists in django.contrib.auth.models.User

    birthday = models.DateField(verbose_name="Født", blank=True, null=True)

    study = models.CharField(max_length=60, blank=True, verbose_name="Studieretning")
    studentnumber = models.CharField(max_length=20, verbose_name="Årskortnummer", unique=True)

    gender = models.CharField(max_length=1, choices=(('m', 'Mand',),('f','Kvinde',),), default='m')

    picture = models.ImageField(
            upload_to=tutorpicture_upload_to,
            blank=True,
            )

    def __unicode__(self):
        if self.user:
            return unicode(self.studentnumber)+u' '+unicode(self.get_full_name())+u' '+unicode(self.user.username)
        else:
            return unicode(self.studentnumber)+u' '+unicode(self.get_full_name())+u' (no user)'

    class Meta:
        verbose_name = 'tutorprofil'
        verbose_name_plural = verbose_name + 'er'

    def get_full_name(self):
        if self.user:
            return self.user.get_full_name()
        if self.activation:
            return self.activation.get_full_name()
        return None

# "Arbejdsgruppe"
class TutorGroup(models.Model):
    handle = models.CharField(max_length=20, primary_key=True, verbose_name="Kort navn",
        help_text="Bruges i gruppens emailadresse")
    name = models.CharField(max_length=40, verbose_name="Langt navn",
        help_text="Vises på hjemmesiden")
    visible = models.BooleanField()

    def __unicode__(self):
        return self.handle

    class Meta:
        ordering = ['name', 'handle']
        verbose_name = 'arbejdsgruppe'
        verbose_name_plural = verbose_name + 'r'

# "Rushold"
class RusClass(models.Model):
    id = models.AutoField(primary_key=True)
    handle = models.CharField(max_length=20, verbose_name="Navn",
        help_text="Bruges i holdets emailadresse")
    year = models.IntegerField(verbose_name="Tutorår")

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

    def is_tutorbest(self):
        import auth
        return bool(auth.is_tutorbest(self))
    is_tutorbest.boolean = True

    def __unicode__(self):
        return unicode(self.profile)+' ('+unicode(self.year)+')'

    class Meta:
        ordering = ['-year']
        verbose_name = 'tutor'
        verbose_name_plural = verbose_name + 'er'

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

    def __unicode__(self):
        return unicode(self.title)+u' '+unicode(self.tutor)

    class Meta:
        ordering = ['tutor__year', 'position']
        verbose_name = 'bestyrelsesmedlem'
        verbose_name_plural = verbose_name + 'mer'


# Freshman semester of a user for a single year
class Rus(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(TutorProfile)
    year = models.IntegerField(verbose_name="Tutorår")
