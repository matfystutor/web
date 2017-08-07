"""
Set the 'study' field of TutorProfile objects
based on the rusclass of associated Rus objects.

Mathias Rav, February 2015
"""


import os
import sys
import datetime
import subprocess
import collections

import codecs
sys.stdin = codecs.getreader('utf8')(sys.stdin)
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mftutor.settings'

import django.db.utils
from django.template import Template, Context
from django.template.loader import get_template
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.mail import get_connection

from mftutor.tutor.models import *

YEAR = 2015

tutors = TutorProfile.objects.filter(tutor__year__exact=YEAR, study='')

rus = list(Rus.objects.filter(profile__in=tutors).order_by('-year'))

assignments = []

for tutor in tutors:
    r = next(x for x in rus if x.profile == tutor)
    rusclass = r.rusclass.internal_name
    study = re.sub(r' *[0-9]*$', '', rusclass)
    assignments.append((study, tutor))

assignments = sorted(assignments)

if assignments:
    for study, tutor in assignments:
        print("%s %s" % (study, tutor.name))
    print("Making the above assignments. Enter to proceed, or Ctrl-C to cancel.")
    sys.stdin.read(1)
    for study, tutor in assignments:
        tutor.study = study
        tutor.save()
