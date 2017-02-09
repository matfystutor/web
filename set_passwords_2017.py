# encoding: utf8
from __future__ import unicode_literals

import os
import json
import codecs
import subprocess

os.environ['DJANGO_SETTINGS_MODULE'] = 'mftutor.settings'

import django

django.setup()

from django.template import Template, Context
from django.template.loader import get_template
from django.core.mail import EmailMessage

from mftutor.tutor.models import TutorProfile, Tutor, TutorGroup


def pwgen(n):
    s = subprocess.check_output(('pwgen', '-nc', '8', str(n)))
    return s.decode('ascii').split()


def main():
    tutors = list(Tutor.members(2017))
    passwords = pwgen(len(tutors))
    output = {}
    users = []
    for tutor, password in zip(tutors, passwords):
        studentnumber = tutor.profile.studentnumber
        if studentnumber == '201400573':
            print("Skip Alexandra")
            output[studentnumber] = 'bla'
            continue
        user = tutor.profile.get_or_create_user()
        output[studentnumber] = password
        user.set_password(password)
        users.append(user)
    with open('passwords_2017.json', 'w') as fp:
        json.dump(output, fp, indent=2)
    # for u in users:
    #     u.save()


if __name__ == '__main__':
    main()
