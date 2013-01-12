# coding: utf-8
# See https://docs.djangoproject.com/en/1.4/topics/auth/
# for a discussion on user profiles and django.contrib.auth

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# User data for the project that does not vary from year to year
class TutorProfile(models.Model):
    id = models.AutoField(primary_key=True)
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

    picture = models.ImageField(upload_to='tutorpics')

    def __unicode__(self):
        return unicode(self.user.get_full_name())+u' '+unicode(self.user.username)

# "Arbejdsgruppe"
class TutorGroup(models.Model):
    handle = models.CharField(max_length=20, primary_key=True, verbose_name="Kort navn",
        help_text="Bruges i gruppens emailadresse")
    name = models.CharField(max_length=40, verbose_name="Langt navn",
        help_text="Vises på hjemmesiden")
    visible = models.BooleanField()

    def __unicode__(self):
        return self.handle

# "Rushold"
class RusClass(models.Model):
    id = models.AutoField(primary_key=True)
    handle = models.CharField(max_length=20, verbose_name="Navn",
        help_text="Bruges i holdets emailadresse")
    year = models.IntegerField(verbose_name="Tutorår")

# Membership of a user for a single year
class Tutor(models.Model):
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
        import tutor.auth
        return tutor.auth.is_tutorbest(self)

    def __unicode__(self):
        return unicode(self.profile)+' ('+unicode(self.year)+')'

class BoardMember(models.Model):
    id = models.AutoField(primary_key=True)
    tutor = models.ForeignKey(Tutor)
    position = models.IntegerField(verbose_name="Rækkefølge")
    title = models.CharField(max_length=50, verbose_name="Titel")

    def __unicode__(self):
        return unicode(self.title)+u' '+unicode(self.tutor)

# Freshman semester of a user for a single year
class Rus(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(TutorProfile)
    year = models.IntegerField(verbose_name="Tutorår")
