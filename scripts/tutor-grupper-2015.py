"""
Suppose tutor-grupper-2015.txt contains lines like the following:

201205387	Nikolai Houlberg Øllegaard	web
20103940	Mathias Rav	buret,*web
201205992	Biodynamisk	buret
201205964	Knud Valdemar Trøllund Lassen	buret,*hytter

Each line contains three fields separated by tabs:
(student number, name, groups)
where groups is a comma-separated list of TutorGroup handles,
and an asterisk prefix means the person is the TutorGroupLeader.

This script creates Tutor objects and sends out emails
(found in TutorProfile objects).
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
from django.core.mail import EmailMessage
from django.core.mail import get_connection

from mftutor.tutor.models import *


YEAR = 2015

group_members = collections.defaultdict(list)

tutors = []

one = two = buret = 0

with codecs.open('tutor-grupper-2015.txt', encoding='utf8') as fp:
    for line in fp:
        sn, navn, groups = line.strip('\n').split('\t')
        groups = groups.split(',')
        if 'rejected' in groups:
            pass
        elif 'buret' in groups:
            buret += 1
        elif len(groups) == 1:
            one += 1
        elif len(groups) == 2:
            two += 1
        else:
            raise ValueError("%s has groups %s" % (navn, groups))
        group_handles = []
        leader_handles = []
        for group in groups:
            if group[0] == '*':
                group_members[group[1:]].append((sn, navn, True))
                group_handles.append(group[1:])
                leader_handles.append(group[1:])
            else:
                group_members[group].append((sn, navn, False))
                group_handles.append(group)
        tutors.append({
            'name': navn,
            'studentnumber': sn,
            'group_handles': group_handles,
            'leader_handles': leader_handles,
            'rejected': 'rejected' in groups,
        })

def print_counts():
    print("Buret: %s En gruppe: %s To grupper: %s I alt: %s" %
          (buret, one, two, buret + one + two))

def print_invalid_group_leader():
    for group, members in sorted(group_members.items(), key=lambda x: x[0]):
        if group == 'rejected':
            continue
        gl = [navn for sn, navn, ans in members if ans]
        if len(gl) != 1:
            print("%s: %s" % (group, gl))

def print_groups():
    for group, members in sorted(group_members.items(), key=lambda x: x[0]):
        print('%s: %s' % (group, ', '.join(
            '%s%s' % ('*' if ans else '', navn)
            for sn, navn, ans in sorted(members, key=lambda x: (not x[2], x[1])))))
        print('')

def resolve_profiles():
    studentnumbers = [o['studentnumber'] for o in tutors]
    profiles = TutorProfile.objects.filter(studentnumber__in=studentnumbers)
    d = dict((tp.studentnumber, tp) for tp in profiles)
    for o in tutors:
        o['tp'] = d[o['studentnumber']]

def resolve_groups():
    group_sets = [set(o['group_handles']) for o in tutors if not o['rejected']]
    handles = sorted(set.union(*group_sets)) + ['alle', 'gruppeansvarlige']
    groups = TutorGroup.objects.filter(handle__in=handles)
    d = dict((g.handle, g) for g in groups)
    for handle, g in d.items():
        if not g.visible and g.handle not in ('alle', 'gruppeansvarlige'):
            print("Invisible group: %s" % g)
    alle = d['alle']
    leader = d['gruppeansvarlige']
    for o in tutors:
        if not o['rejected']:
            o['groups'] = [d[g] for g in o['group_handles']]
            o['groups'].append(alle)
            if o['leader_handles']:
                o['leader'] = [d[g] for g in o['leader_handles']]
                o['groups'].append(leader)
            else:
                o['leader'] = []


def make_objects():
    tutor_qs = Tutor.objects.filter(year=YEAR)
    tutor_objects = dict((tu.profile.studentnumber, tu) for tu in tutor_qs)
    tgl_qs = TutorGroupLeader.objects.filter(year=YEAR)
    tgl = dict((o.group.handle, o) for o in tgl_qs)
    tgl_total = tu_created = tu_total = 0
    tgl_exist = []
    for o in tutors:
        o['objects'] = []
        if not o['rejected']:
            tu_total += 1
            try:
                tu = tutor_objects[o['studentnumber']]
            except KeyError:
                tu = Tutor(year=YEAR, profile=o['tp'])
                tu_created += 1
            o['tutor_object'] = tu
            o['objects'].append(tu)
            for gr in o['leader']:
                a = tgl.get(gr.handle)
                if a and a.tutor != tu:
                    print("TutorGroupLeader already exists! %s %s %s" % (a.pk, a.tutor, tu))
                if not a:
                    a = TutorGroupLeader(tutor=tu, group=gr, year=YEAR)
                else:
                    tgl_exist.append(gr.handle)
                o['objects'].append(a)
                tgl_total += 1
    print("%d out of %d Tutor objects must be created" % (tu_created, tu_total))
    print("Of %d TutorGroupLeader, %d exist: [%s]" % (tgl_total, len(tgl_exist), ' '.join(tgl_exist)))


def generate_passwords(pw_length, num_pw):
    p = subprocess.Popen(
        ('pwgen',
         '--capitalize',
         '--numerals',
         str(pw_length),
         str(num_pw)),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        universal_newlines=True)
    p.stdin.close()
    passwords = p.stdout.read().split()
    p.stdout.close()
    p.wait()
    return passwords


def choose_passwords():
    no_password = []
    for o in tutors:
        password = o['tp'].user.password
        if password == '':
            raise ValueError('Password field is blank!')
        elif password == '!':
            no_password.append(o)
        else:
            o['password'] = ''
    pw_length = 8
    num_pw = len(no_password)
    passwords = generate_passwords(pw_length, num_pw)
    for o, password in zip(no_password, passwords):
        o['password'] = password
        print('%-9s %s %s' % (o['studentnumber'], o['password'], o['name']))


def create_emails():
    rejected = get_template('emails/afvist.txt')
    buret = get_template('emails/buret.txt')
    buretansv = get_template('emails/buretansv.txt')
    ansv = get_template('emails/ansv.txt')
    ordinary = get_template('emails/tutors.txt')

    webfar = 'Mathias Rav'
    sender_email = 'webfar@matfystutor.dk'

    for o in tutors:
        groups = [g.name for g in o.get('groups', [])
                  if g.handle not in 'alle gruppeansvarlige'.split()]
        if o['rejected']:
            subject = 'Fra tutorgruppen'
            sender = '"Mat/Fys-Tutorgruppen" <best@matfystutor.dk>'
            body = rejected.render(Context(dict(
                navn=o['tp'].name,
                year=YEAR,
            )))

        elif 'buret' in o['group_handles']:
            subject = 'Du er blevet tutor!'
            sender = '"%s" <%s>' % (webfar, sender_email)
            if o['leader_handles']:
                leader_group, = o['leader']
                body = buretansv.render(Context(dict(
                    navn=o['name'],
                    studentnumber=o['studentnumber'],
                    year=YEAR,
                    webfar=webfar,
                    groups=' og '.join(g for g in groups if g != 'Buret'),
                    group=leader_group.name,
                    password=o['password'],
                )))

            else:
                body = buret.render(Context(dict(
                    navn=o['name'],
                    studentnumber=o['studentnumber'],
                    year=YEAR,
                    webfar=webfar,
                    groups=' og '.join(g for g in groups if g != 'Buret'),
                    password=o['password'],
                )))

        else:
            if o['leader_handles']:
                subject = 'Du er blevet tutor!'
                sender = '"%s" <%s>' % (webfar, sender_email)
                leader_group, = o['leader']
                body = ansv.render(Context(dict(
                    navn=o['name'],
                    studentnumber=o['studentnumber'],
                    year=YEAR,
                    webfar=webfar,
                    groups=' og '.join(g for g in groups),
                    group=leader_group.name,
                    password=o['password'],
                )))

            else:
                subject = 'Du er blevet tutor!'
                sender = '"%s" <%s>' % (webfar, sender_email)
                body = ordinary.render(Context(dict(
                    navn=o['name'],
                    studentnumber=o['studentnumber'],
                    year=YEAR,
                    webfar=webfar,
                    groups=' og '.join(g for g in groups),
                    password=o['password'],
                )))

        o['email'] = EmailMessage(
            subject=subject,
            from_email=sender,
            body=body,
            to=['"%s" <%s>' % (o['tp'].name, o['tp'].email)],
        )


def print_emails():
    for o in tutors:
        e = o['email']
        print('From: {sender}\nTo: {to}\nSubject: {subject}\n\n{body}'.format(
            sender=e.from_email,
            to=e.to[0],
            subject=e.subject,
            body=e.body))
        print(79*'-')


email_backend_type = 'django.core.mail.backends.smtp.EmailBackend'

def send_emails(dry):
    if dry:
        print("Send emails dry run")
    email_backend = get_connection(backend=email_backend_type)
    messages = []
    for o in tutors:
        e = o['email']
        print("Send email To: %s Subject: %s" % (e.to, e.subject))
        if not dry:
            messages.append(e)
    res = email_backend.send_messages(messages)
    print("email_backend.send_messages returned %s" % res)


def save_objects(dry):
    if dry:
        print("SAVE OBJECTS dry run")
    else:
        print("SAVE OBJECTS for real")
    for o in tutors:
        for obj in o['objects']:
            if not dry:
                if isinstance(obj, TutorGroupLeader):
                    obj.tutor = o['tutor_object']
                try:
                    obj.save()
                except django.db.utils.IntegrityError:
                    print("Failed to save %s" % obj)
                    raise
        if not o['rejected']:
            o['tutor_object'].groups.add(*o['groups'])
    for o in tutors:
        if o['password']:
            if not dry:
                o['tp'].user.set_password(o['password'])
                o['tp'].user.save()
            print("Password changed for %s to %s" % (o['tp'].studentnumber, o['password']))


if __name__ == "__main__":
    print("Script start %s" % datetime.datetime.now())
    print_counts()
    print_invalid_group_leader()
    resolve_profiles()
    resolve_groups()
    make_objects()
    choose_passwords()
    create_emails()
    print_emails()
    save_objects(dry=False)
    send_emails(dry=False)
