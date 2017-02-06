# coding: utf-8
from __future__ import unicode_literals

from django.db import models

from mftutor.tutor.models import TutorGroup, TutorProfile


class EmailTemplate(models.Model):
    year = models.IntegerField(verbose_name="Tutorår")
    text = models.TextField()
    subject = models.CharField(max_length=200)
    name = models.CharField(max_length=200)


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
    tutortype = models.CharField(max_length=20)

    email_template = models.ForeignKey(
        EmailTemplate, null=True, blank=True, on_delete=models.SET_NULL)

    groups = models.ManyToManyField(
        TutorGroup, through='TutorApplicationGroup')
    assigned_groups = models.ManyToManyField(
        TutorGroup, related_name='tutorapplication_assigned_set')
    profile = models.ForeignKey(TutorProfile, null=True, blank=True)

    comments = models.TextField(blank=True)


class TutorApplicationGroup(models.Model):
    application = models.ForeignKey(TutorApplication)
    group = models.ForeignKey(TutorGroup)
    priority = models.IntegerField()

    class Meta:
        ordering = ('priority',)


class AssignedGroupLeader(models.Model):
    application = models.ForeignKey(TutorApplication)
    group = models.OneToOneField(TutorGroup)
