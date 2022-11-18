import subprocess
import csv
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'mftutor.settings'

import django

django.setup()

from django.core.exceptions import ValidationError
from django.template.loader import get_template
from django.core.mail import EmailMessage

from mftutor.tutor.models import TutorProfile, Tutor, TutorGroup


email_backend_type = 'django.core.mail.backends.smtp.EmailBackend'


def send_messages(messages, backend_type):
    from django.core.mail import get_connection

    email_backend = get_connection(backend=backend_type)

    return email_backend.send_messages(messages)


YEAR = 2018

TRANSLATE = {
    'toe-matoek': 'toematoek',
    'wiki': 'hacker',
    'evaluering': 'eval',
    'rkfw': 'rkfw-rus2tursguide',
    'toe-nano': 'toenano',
    'toe-dat': 'toedat',
    'toe-mat': 'toemat',
    'toe-fysik': 'toefysik',
    'tutorbest': 'best',
}


def read_csv(filename):
    with open(filename, newline='') as fp:
        # Read each line from the CSV
        reader = iter(csv.reader(fp, dialect='excel'))
        # The first line is the CSV header
        input_header = next(reader)

        header_fields = {
            "Navn": "name",
            "Mobil": "phone",
            "E-mail-adresse": "email",
            "Årskortnummer": "studentnumber",
            "Studieretning": "study",
            "Tutortype": "tutortype",
            "Grupper": "groups",
            "Gruppeansvarlig": "leader",
        }
        expected_header = set(header_fields.keys())
        header_set = set(input_header)

        if not expected_header.issubset(header_set):
            raise ValidationError(
                "Manglende header-felter i CSV data: %r" %
                (sorted(expected_header - header_set),))

        result = []
        for row in reader:
            row_values = [c.strip() for c in row]
            if not any(row_values):
                # Skip rows containing only blanks
                continue

            row_dict = {}
            for h, v in zip(input_header, row_values):
                try:
                    k = header_fields[h]
                except KeyError:
                    # Header not in header_fields: ignore value
                    continue
                row_dict[k] = v

            result.append(row_dict)

        return result


def get_existing_tutorprofiles(studentnumbers):
    # 2. Retrieve existing TutorProfiles based on studentnumbers
    tutorprofiles = TutorProfile.objects.filter(
        studentnumber__in=studentnumbers)
    tp_dict = {
        tp.studentnumber: tp
        for tp in tutorprofiles
    }
    return tp_dict


def find_new_tutors(studentnumbers):
    tutorprofiles = TutorProfile.objects.filter(
        studentnumber__in=studentnumbers)
    tutorprofiles = tutorprofiles.filter(tutor__isnull=True)
    return list(tutorprofiles)


def generate_passwords(new_tutors):
    output = subprocess.check_output(['pwgen', '8', str(len(new_tutors))], universal_newlines=True)
    lines = output.split()
    assert len(lines) == len(new_tutors)
    passwords = {tp.studentnumber: password
                 for tp, password in zip(new_tutors, lines)}

    def save_passwords():
        for tp, password in zip(new_tutors, lines):
            user = tp.get_or_create_user()
            user.set_password(password)
            user.save()

    return passwords, save_passwords


def get_tutorgroup_dict():
    tutorgroups = TutorGroup.objects.filter(visible=True, year=YEAR)
    tg_dict = {
        tg.handle: tg
        for tg in tutorgroups
    }
    return tg_dict


def find_tutorgroups(rows):
    tg_dict = get_tutorgroup_dict()
    tutorgroups = {}
    leaders = {}
    data_handles = set(TRANSLATE.get(handle.strip(), handle.strip())
                       for row in rows
                       for handle in row['groups'].split(',') + [row['leader']]
                       if handle.strip())
    missing = data_handles - set(tg_dict)
    if missing:
        raise Exception("Missing handles: %r" % (missing,))
    for row in rows:
        try:
            groups = []
            group_handles = row['groups'].split(',') if row['groups'] else ()
            for handle in group_handles:
                handle = TRANSLATE.get(handle.strip(), handle.strip())
                group = tg_dict[handle]
                groups.append(group)
            if row['tutortype'] == 'Buret (kræver tutorerfaring)':
                groups.append(tg_dict['buret'])
            tutorgroups[row['studentnumber']] = groups
            if row['leader']:
                handle = TRANSLATE.get(row['leader'], row['leader'])
                groups.append(tg_dict['gruppeansvarlige'])
                leaders[row['studentnumber']] = tg_dict[handle]
        except Exception:
            print(row)
            raise
    return tutorgroups, leaders 


def create_emails(passwords, tp_dict, tutorgroups, leaders):
    emails = []

    for tp in tp_dict.values():
        groups = tutorgroups[tp.studentnumber] 

        leader = leaders.get(tp.studentnumber)
        # arbejdstutor = any(g.handle == 'arbejdstutor' for g in groups)
        buret = any(g.handle == 'buret' for g in groups)
        normal_groups = [g for g in groups
                         if g.handle not in ('arbejdstutor', 'buret', 'gruppeansvarlige')]
        group_names = [g.name for g in normal_groups]
        ansv_names = [leader.name] if leader else []
        context = dict(
            navn=tp.name.strip(),
            year=YEAR,
            studentnumber=tp.studentnumber,
            groups=' og '.join(group_names),
            webfar='Thomas Skovlund Hansen',
            password=passwords.get(tp.studentnumber),
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
        # elif arbejdstutor:
        #     if ansv_names:
        #         tpl = 'arbejdansv.txt'
        #         subject = 'Du er blevet gruppeansvarlig!'
        #     else:
        #         tpl = 'arbejd.txt'
        #         subject = 'Du er blevet tutor!'
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
            from_email='"Mat/Fys-Tutorforeningen" <best@matfystutor.dk>',
            to=[tp.email],
        )

        emails.append(email)

    # emails = [
    #     email
    #     for email in emails
    #     if 'nikolai@oellegaard.dk' in email.to
    # ]

    with open('email%s.txt' % YEAR, 'w') as fp:
        for email in emails:
            fp.write(79*'=' + '\n')
            fp.write("Fra: %s\n" % email.from_email)
            fp.write("Til: %s\n" % email.to[0])
            fp.write("Emne: %s\n" % email.subject)
            fp.write('\n%s\n' % (email.body))

    return emails


def create_tutors(tp_dict):
    existing = {tutor.profile.studentnumber: tutor
                for tutor in Tutor.members(YEAR)}
    create = []
    for studentnumber, tp in tp_dict.items():
        if studentnumber in existing:
            continue
        t = Tutor(year=YEAR, profile=tp)
        create.append(t)
        existing[studentnumber] = t

    def save_tutors():
        for tutor in create:
            tutor.save()
    
    return existing, save_tutors


def save_groups(tutor_dict, tutorgroups, leaders):
    for studentnumber, tutor in tutor_dict.items():
        tutor.groups.add(*tutorgroups[studentnumber])
        leader = leaders.get(studentnumber)
        if leader:
            leader.leader = tutor
            leader.save()


def output_mismatched_data(tp_dict, rows):
    with open('mismatched_data%s.txt' % YEAR, 'w') as fp:
        for row in rows:
            tp = tp_dict[row['studentnumber']]
            if tp.email != row['email'] or tp.name != row['name']:
                data = (tp.studentnumber, tp.name, tp.email,
                        row['name'], row['email'])
                fp.write('\t'.join(data) + '\n')


def set_profile_data(tp_dict, rows):
    for row in rows:
        tp = tp_dict[row['studentnumber']]
        tp.email = row['email']
        tp.name = row['name']
        tp.phone = row['phone']
        tp.study = row['study']


def main():
    rows = read_csv('tutors%s.csv' % YEAR)
    studentnumbers = [row['studentnumber'] for row in rows]
    tp_dict = get_existing_tutorprofiles(studentnumbers)
    missing = set(studentnumbers) - set(tp_dict)
    assert not missing, missing
    output_mismatched_data(tp_dict, rows)
    set_profile_data(tp_dict, rows)
    tutorgroups, leaders = find_tutorgroups(rows)
    new_tutors = find_new_tutors(studentnumbers)
    passwords, save_passwords = generate_passwords(new_tutors)
    emails = create_emails(passwords, tp_dict, tutorgroups, leaders)
    tutor_dict, save_tutors = create_tutors(tp_dict)

    if True:
        return

    for tp in tp_dict.values():
        tp.save()
    save_passwords()
    save_tutors()
    save_groups(tutor_dict, tutorgroups, leaders)
    send_messages(emails, email_backend_type)

if __name__ == "__main__":
    main()
