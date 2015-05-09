# coding: utf-8
from __future__ import unicode_literals

from django.db import models

from mftutor.tutor.models import TutorGroup, TutorProfile


class TutorApplication(models.Model):
    year = models.IntegerField(verbose_name="Tutorår")

    name = models.CharField(max_length=60)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=75)
    studentnumber = models.CharField(max_length=20)
    study = models.CharField(max_length=60)
    previous_tutor_years = models.IntegerField()
    rus_year = models.IntegerField()
    new_password = models.BooleanField()
    accepted = models.BooleanField(default=True)
    buret = models.BooleanField()

    groups = models.ManyToManyField(TutorGroup, through='TutorApplicationGroup')
    profile = models.ForeignKey(TutorProfile, null=True, blank=True)

    comments = models.TextField(blank=True)


class TutorApplicationGroup(models.Model):
    application = models.ForeignKey(TutorApplication)
    group = models.ForeignKey(TutorGroup)
    priority = models.IntegerField()
