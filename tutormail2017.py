# encoding: utf8
from __future__ import unicode_literals

import os
import json
import codecs

os.environ['DJANGO_SETTINGS_MODULE'] = 'mftutor.settings'

import django

django.setup()

from django.template import Template, Context
from django.template.loader import get_template
from django.core.mail import EmailMessage

from mftutor.tutor.models import TutorProfile, Tutor, TutorGroup


email_backend_type = 'django.core.mail.backends.smtp.EmailBackend'


def send_messages(messages, backend_type):
    from django.core.mail import get_connection

    email_backend = get_connection(backend=backend_type)

    return email_backend.send_messages(messages)


YEAR = 2017


def main():
    with open('passwords_2017.json') as fp:
        passwords = json.load(fp)
    emails = []
    for tutor in Tutor.members(2017):
        tp = tutor.profile
        groups = tutor.groups.filter(visible=True)

        arbejdstutor = any(g.handle == 'arbejdstutor' for g in groups)
        buret = any(g.handle == 'buret' for g in groups)
        normal_groups = [g for g in groups
                         if g.handle not in ('arbejdstutor', 'buret')]
        group_names = [g.name for g in normal_groups]
        ansv_names = [g.name for g in normal_groups if g.leader == tutor]
        context = dict(
            navn=tp.name.strip(),
            year=YEAR,
            studentnumber=tp.studentnumber,
            groups=' og '.join(group_names),
            webfar='Alexandra Hou',
            password=passwords[tp.studentnumber],
            group=' og '.join(ansv_names),
        )

        # afvist.txt: navn, year
        # ansv.txt: navn, year, studentnumber, password, groups, group, webfar
        # buret.txt: navn, groups, studentnumber, password, webfar
        # buretansv.txt: navn, groups, studentnumber, password, group, webfar
        # tutors.txt: navn, year, studentnumber, password, groups, webfar

        if buret:
            if ansv_names:
                tpl = 'buretansv.txt'
                subject = 'Du er blevet gruppeansvarlig!'
            else:
                tpl = 'buret.txt'
                subject = 'Du er blevet tutor!'
        elif arbejdstutor:
            if ansv_names:
                tpl = 'arbejdansv.txt'
                subject = 'Du er blevet gruppeansvarlig!'
            else:
                tpl = 'arbejd.txt'
                subject = 'Du er blevet tutor!'
        else:
            if ansv_names:
                tpl = 'ansv.txt'
                subject = 'Du er blevet gruppeansvarlig!'
            else:
                tpl = 'tutors.txt'
                subject = 'Du er blevet tutor!'

        tpl = get_template('emails/%s' % tpl)

        email_body = tpl.render(context)

        email = EmailMessage(
            subject=subject,
            body=email_body,
            from_email='"Alexandra Hou" <best@matfystutor.dk>',
            to=[tp.email],
        )

        emails.append(email)

    # emails = [
    #     email
    #     for email in emails
    #     if 'nikolai@oellegaard.dk' in email.to
    # ]

    with codecs.open('email2017.txt', 'w', encoding='utf-8') as fp:
        for email in emails:
            fp.write(79*'=' + '\n')
            fp.write("Fra: %s\n" % email.from_email)
            fp.write("Til: %s\n" % email.to[0])
            fp.write("Emne: %s\n" % email.subject)
            fp.write('\n%s\n' % (email.body))

    # send_messages(emails, email_backend_type)


if __name__ == '__main__':
    main()
