# coding: utf-8
# See https://docs.djangoproject.com/en/1.4/topics/auth/
# for a discussion on user profiles and django.contrib.auth

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# User data for the project that does not vary from year to year
class TutorProfile(models.Model):
    user = models.OneToOneField(User)

    #name = models.CharField(max_length=60, verbose_name="Fulde navn")
    # first name and last name exist in User
    street = models.CharField(max_length=80, verbose_name="Adresse")
    city = models.CharField(max_length=40, verbose_name="Postnr. og by")
    phone = models.CharField(max_length=20, verbose_name="Telefonnr.")
    #email = models.EmailField(verbose_name="E-mailadresse")
    # Email address exists in django.contrib.auth.models.User

    birthday = models.DateField(verbose_name="Født", blank=True, null=True)

    study = models.CharField(max_length=20, verbose_name="Studieretning")
    studentnumber = models.CharField(max_length=20, verbose_name="Årskortnummer", unique=True)

    gender = models.CharField(max_length=1, choices=(('m', 'Mand',),('f','Kvinde',),))

    def __unicode__(self):
        return self.user.username

def create_tutor_profile(sender, instance, created, **kwargs):
    if created:
        TutorProfile.objects.create(user=instance)

post_save.connect(create_tutor_profile, sender=User)

# "Arbejdsgruppe"
class TutorGroup(models.Model):
    handle = models.CharField(max_length=20, primary_key=True, verbose_name="Kort navn",
        help_text="Bruges i gruppens emailadresse")
    name = models.CharField(max_length=40, verbose_name="Langt navn",
        help_text="Vises på hjemmesiden")

# "Rushold"
class RusClass(models.Model):
    handle = models.CharField(max_length=20, verbose_name="Navn",
        help_text="Bruges i holdets emailadresse")
    year = models.IntegerField(verbose_name="Tutorår")

# Membership of a user for a single year
class Tutor(models.Model):
    profile = models.ForeignKey(TutorProfile)
    year = models.IntegerField(verbose_name="Tutorår")
    groups = models.ManyToManyField(TutorGroup, verbose_name="Arbejdsgrupper", blank=True)
    early_termination = models.DateTimeField(null=True, blank=True, verbose_name="Ekskluderet",
        help_text="Tidspunkt i året hvor tutoren stopper i foreningen")
    early_termination_reason = models.TextField(null=True, blank=True, verbose_name="Eksklusionsårsag",
        help_text="Årsag til at tutoren stopper")
    rusclass = models.ForeignKey(RusClass, null=True, blank=True)

    def __unicode__(self):
        return str(self.profile)+' (tutor in '+str(self.year)+')'

# Freshman semester of a user for a single year
class Rus(models.Model):
    profile = models.ForeignKey(TutorProfile)
    year = models.IntegerField(verbose_name="Tutorår")

def user_tutor_data(user):
    if user is None or not user.is_authenticated():
        return {'err': 'failauth'}
    if not user.is_active:
        return {'err': 'djangoinactive'}
    try:
        profile = user.get_profile()
    except TutorProfile.DoesNotExist:
        return {'err': 'notutorprofile'}
    try:
        tut = Tutor.objects.get(profile=profile, year=2012)
    except Tutor.DoesNotExist:
        return {'err': 'notutoryear'}
    return {'err': None, 'data': {'tutorprofile': profile, 'tutor': tut}}
