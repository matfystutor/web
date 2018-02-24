# encoding: utf8
NOPE

import os
import sys  
import json
import codecs
import pprint
import subprocess

import csv

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


email_backend_type = 'django.core.mail.backends.smtp.EmailBackend'


def send_messages(messages, backend_type):
    from django.core.mail import get_connection

    email_backend = get_connection(backend=backend_type)

    return email_backend.send_messages(messages)





group_aliases = {
    "Bur": "buret",
    "CS-lab": "cslab",
    "Dias - CS": "csdias",
    "Dias - IFA": "ifadias",
    "Dias - IMF": "imfdias",
    "Evaluering": "eval",
    "Høstfest": "hoestfest",
    "Hytte": "hytte",
    "IFA-lab": "ifalab",
    "iNano-lab": "nanolab",
    "Indkøb": "inko",
    "Latex": "latex",
    "LaTeX": "latex",
    "Korrektur": "korrektur",
    "Legebog": "legebog",
    "Lokaler": "lokale",
    "ParXafari": "parxafari",
    "Praktiske Grise": "grise",
    "RKFL^3": "rkfl3",
    "RKFW": "rkfw",
    "Rus2Turs-guide": "rus2turguide",
    "Rusguide": "rusguide",
    "Rusteater": "rusteater",
    "Sangbog": "sangbog",
    "SOL": "sol",
    "Sportsdag": "sportsdag",
    "TØ i rusdagene - datalogi": "datalogitoe",
    "TØ i rusdagene - it": "toeit",
    "TØ i rusdagene - IT": "toeit",
    "TØ i rusdagene - mat/øk": "toematoek",
    "TØ i rusdagene - Matematik": "toemat",
    "TØ i rusdagene - nano": "toenano",
    "TØ i rusdagene - Fysik": "toefysik",
    "Tutorbog": "tutorbog",
    "Tutorfest": "tutorfest",
    "Tutor-smiley": "tutorsmiley",
    "Web": "web",
    "Wiki": "wiki",
}


with open('applications.csv', 'rb') as application_file:
    reader = csv.reader(application_file, dialect='excel-tab')
    rows = [[c.decode("utf-8") for c in row] for row in reader]

    input_header = rows[0]
    rows = rows[1:]
    entries = [dict(zip(input_header, row)) for row in rows]
    entries = [
        entry for entry in entries
        if entry['Timestamp'] != ''
        and entry['Fulde navn'] != ''
    ]

    pp = pprint.PrettyPrinter(indent=4)

    approved_entries = []
    denied_entries = []

    for entry in entries:
    	if entry["GRUPPE 1"]:
    		approved_entries.append(entry)
    	else:
    		denied_entries.append(entry)

    for entry in approved_entries:
    	gruppe1 = entry["GRUPPE 1"]
    	gruppe2 = entry["GRUPPE 2"]
    	navn = entry["Fulde navn"]

    	# print("%s\t%s" % (navn, gruppe1))

    print("%s approved, %s rejected" % (len(approved_entries), len(denied_entries)))

    by_sn = {}
    for entry in entries:
        by_sn.setdefault(entry['Årskortnummer'], [])
        by_sn[entry['Årskortnummer']].append(entry)
    dup = [entry for k, v in by_sn.items() for entry in v if len(v) != 1]
    if dup:
        print(json.dumps(dup, indent=2, sort_keys=True))
        raise Exception("Dup")
    if '' in by_sn:
        raise Exception("Blank studentnumber")

    tutorprofiles = TutorProfile.objects.filter(studentnumber__in=by_sn.keys())
    tutorprofiles_by_sn = {
        tp.studentnumber: tp
        for tp in tutorprofiles}

    # Check missing
    found = [tp.studentnumber for tp in tutorprofiles]
    missing = set(by_sn.keys()) - set(found)
    if missing:
        raise Exception("Missing: %s" % ', '.join(missing))

    # Check emails
    for tp in tutorprofiles:
        entry, = by_sn[tp.studentnumber]
        entry_email = entry['E-mailadresse'].strip().lower()
        tp_email = tp.email.strip().lower()
        if '' != entry_email != tp_email:
            # tp.email = entry_email
            # tp.save()
            print("%s\t%s\t%s" % (tp.studentnumber, entry_email, tp.email))

    # Create Tutor objects
    existing_tutor = Tutor.objects.filter(
        year=2016, profile__studentnumber__in=by_sn.keys())
    for tu in existing_tutor:
        # print(tu)
        pass
    existing_sn = {
        tu.profile.studentnumber: tu
        for tu in existing_tutor
    }

    prev_tutor = Tutor.objects.filter(
        year__lt=2016, profile__studentnumber__in=by_sn.keys())
    prev_tutor_sn = set(tu.profile.studentnumber for tu in prev_tutor)

    passwords = pwgen(200)

    group_by_handle = {
        g.handle: g for g in TutorGroup.objects.filter(
            year=2016, handle__in=group_aliases.values())
    }

    new_tutor = []
    new_password = []
    new_groups = []
    group_leaders = []
    for entry in approved_entries:
        sn = entry['Årskortnummer']
        tp = tutorprofiles_by_sn[sn]
        entry['tutorprofile'] = tp
        if sn not in existing_sn:
            tu = Tutor(year=2016, profile=tp)
            new_tutor.append(tu)
            # print(new_tutor[-1])
            # tu.save()
            raise Exception("Did not exist")
        else:
            tu = existing_sn[sn]

        group_names = [entry['GRUPPE 1'], entry['GRUPPE 2']]
        group_names = [s for s in group_names if s != '-']
        group_handles = [group_aliases[g] for g in group_names]
        group_objects = [group_by_handle[g] for g in group_handles]

        for g in group_objects:
            new_groups.append((tu, g))

        if entry['Ansvarlig 1']:
            group_leaders.append((tu, group_objects[0]))
        if entry['Ansvarlig 2']:
            group_leaders.append((tu, group_objects[1]))

        while not tp.user:
            tp.get_or_create_user()

        if sn not in prev_tutor_sn or tp.user.password == '' or tp.user.password == '!':
            p = passwords.pop()
            new_password.append((tp.user, p))
            entry['password'] = p
        else:
            entry['password'] = None
    for u, p in new_password:
        print("username=%s password=%s" % (u.username, p))
        # u.set_password(p)
        # u.save()
    # print(new_groups)
    # for tu, g in new_groups:
    #     tu.groups.add(g)
    # print(group_leaders)
    for tu, g in group_leaders:
        g.leader = tu
        g.save()

    emails = []
    for entry in approved_entries:
        tp = entry['tutorprofile']
        group_names = [entry['GRUPPE 1'], entry['GRUPPE 2']]
        group_names = [s for s in group_names if s != '-']
        ansv_names = []
        if entry['Ansvarlig 1']:
            ansv_names.append(entry['GRUPPE 1'])
        if entry['Ansvarlig 2']:
            ansv_names.append(entry['GRUPPE 2'])
        context = dict(
            navn=tp.name.strip(),
            year=2016,
            studentnumber=tp.studentnumber,
            groups=' og '.join(group_names),
            webfar='Nikolai Øllegaard',
            password=entry['password'],
            group=' og '.join(ansv_names),
        )

        # afvist.txt: navn, year
        # ansv.txt: navn, year, studentnumber, password, groups, group, webfar
        # buret.txt: navn, groups, studentnumber, password, webfar
        # buretansv.txt: navn, groups, studentnumber, password, group, webfar
        # tutors.txt: navn, year, studentnumber, password, groups, webfar

        if 'Bur' in group_names:
            group_names = set(group_names) - set(['Bur'])
            context['groups'] = ' og '.join(group_names)
            if ansv_names:
                tpl = 'buretansv.txt'
                subject = 'Du er blevet gruppeansvarlig!'
            else:
                tpl = 'buret.txt'
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
            from_email='"Nikolai Øllegaard" <best@matfystutor.dk>',
            to=[tp.email],
        )

        emails.append(email)

    for entry in denied_entries:
        sn = entry['Årskortnummer']
        tp = tutorprofiles_by_sn[sn]
        tpl = get_template('emails/afvist.txt')
        email_body = tpl.render(dict(navn=entry['Fulde navn'].strip(), year=2016))
        subject = 'Fra tutorgruppen'
        email_address = tp.email

        email = EmailMessage(
            subject=subject,
            body=email_body,
            from_email='"Mat/Fys-Tutorgruppen" <best@matfystutor.dk>',
            to=[tp.email],
        )
        emails.append(email)

    # emails = [
    #     email
    #     for email in emails
    #     if 'nikolai@oellegaard.dk' in email.to
    # ]

    with codecs.open('email2016.txt', 'w', encoding='utf-8') as fp:
        for email in emails:
            fp.write(79*'=' + '\n')
            fp.write("Fra: %s\n" % email.from_email)
            fp.write("Til: %s\n" % email.to[0])
            fp.write("Emne: %s\n" % email.subject)
            fp.write('\n%s\n' % (email.body))

    send_messages(emails, email_backend_type)
