# vim: set fileencoding=utf-8:
from .models import Email
from ..tutor.models import TutorProfile, Tutor, TutorGroup
from ..settings import YEAR

# -----------------------------------------------------------------------------
# Sending Email objects from the database

def get_queryset():
    """Get the emails that are yet to be sent."""
    return Email.objects.filter(sent__exact=None, retain=False, archive=False).order_by('-kind')

def get_one():
    """Get the next email to send."""
    return get_queryset().all()[0]

def make_email_message(mailobj):
    """Takes a models.Email object and turns it into a Django EmailMessage
    object for sending."""

    from django.core.mail import EmailMessage, EmailMultiAlternatives
    import re

    text_content = mailobj.body
    if mailobj.html:
        html_content = text_content
        text_content = re.sub(r'<[^>]*>', '', html_content)
        msg = EmailMultiAlternatives(
                subject=mailobj.subject,
                body=text_content,
                from_email=mailobj.sender,
                to=(mailobj.recipient,))
        msg.attach_alternative(html_content, "text/html")
    else:
        msg = EmailMessage(
                subject=mailobj.subject,
                body=text_content,
                from_email=mailobj.sender,
                to=(mailobj.recipient,))

    return msg

# -----------------------------------------------------------------------------
# Send Django EmailMessage objects.

email_backend_type = 'django.core.mail.backends.smtp.EmailBackend'

def send_messages(messages, backend_type):
    from django.core.mail import get_connection

    email_backend = get_connection(backend=backend_type)

    return email_backend.send_messages(messages)

def send_one():
    o = get_one()
    send_messages((make_email_message(o),), email_backend_type)
    from datetime import datetime
    o.sent = datetime.now()
    o.save()

def send_all(emails):
    from datetime import datetime
    send_messages([make_email_message(o) for o in emails], email_backend_type)
    emails.update(sent=datetime.now())
    print('\n'.join(emails.all()))

def delayed_send_all():
    import time
    from datetime import datetime
    emails = get_queryset()
    for email in emails.all():
        print(email)
        send_messages((make_email_message(email),), email_backend_type)
        email.sent = datetime.now()
        email.save()
        time.sleep(20)

# -----------------------------------------------------------------------------
# Create Email objects in the database based on Tutor objects.

def data_of_studentnumbers(studentnumbers):
    return [{'navn': profile.name, 'email': profile.email}
            for profile in TutorProfile.objects.filter(
                studentnumber__in=studentnumbers).all()]


def read_rejects(filename='rejects.tsv'):
    with open(filename) as fp:
        keys = None
        rows = []
        for i, line in enumerate(fp):
            row = tuple(v.strip() for v in line.split('\t'))
            line = i + 1
            if keys is None:
                keys = tuple(k.lower() for k in row)
            else:
                if len(row) > len(keys):
                    raise ValueError(
                        '%s:%d has %d cells, but we only have %d columns' %
                        (filename, line, len(row), len(keys)))
                rows.append(dict(zip(keys[:len(row)], row)))

    if any(k not in keys for k in 'name email'.split()):
        print('%s needs columns name and email')

    return [(row['name'], row['email']) for row in rows]


def make_mails(not_tutor, joker_numbers, no_mail, passwords):
    """
    not_tutor: list of {navn, email}-dicts (made from data_of_studentnumbers)
    joker_numbers: student numbers of the joker group
    no_mail: student numbers of people not to send mail to
    """

    # template params:
    # navn
    # activation (the link)
    # group1
    # group2

    # buret:
    # navn, activation, groups

    # afvist: navn

    # ansv: navn, group

    # holdtutor
    # buret
    # ansvarlig
    # afvist

    hide_groups = ('alle', 'best', 'gris', 'webfar', 'koor', 'gruppeansvarlige', 'buret')

    all_tutors = Tutor.objects.filter(groups__handle='alle', year=YEAR).exclude(profile__studentnumber__in=no_mail)
    buret = all_tutors.filter(groups__handle='buret').all()
    tutors = all_tutors.exclude(groups__handle='buret').exclude(profile__studentnumber__in=joker_numbers).all()
    group_leaders = [
        tg.leader.profile
        for tg in TutorGroup.objects.filter(year=YEAR)
            .exclude(handle__in=hide_groups, leader__isnull=True)
    ]
    jokers = all_tutors.filter(profile__studentnumber__in=joker_numbers).all()

    webfar = Tutor.objects.filter(year=YEAR, groups__handle='webfar').get().profile
    burfar = TutorGroup.objects.get(handle='buret', year=YEAR).leader.profile

    webfar_sender = '"%s" <webfar@matfystutor.dk>' % webfar.name
    burfar_sender = '"%s" <best@matfystutor.dk>' % burfar.name
    best_sender = '"Mat/Fys-Tutorforeningen" <best@matfystutor.dk>'

    from django.template import Template, Context
    from django.template.loader import get_template
    tpl_buret = get_template('emails/buret.txt')
    tpl_buret_subject = Template('Du er blevet tutor!')
    tpl_holdtutor = get_template('emails/tutors.html')
    tpl_holdtutor_subject = Template('Du er blevet tutor!')
    tpl_ansvarlig = get_template('emails/ansv.txt')
    tpl_ansvarlig_subject = Template('Du er blevet gruppeansvarlig')
    tpl_joker = get_template('emails/jokers.html')
    tpl_joker_subject = Template('Du er blevet tutor!')
    tpl_afvist = get_template('emails/afvist.txt')
    tpl_afvist_subject = Template('Fra tutorforeningen')

    def email(tutor):
        return tutor.profile.email

    def group_queryset(tutor):
        return tutor.groups.filter(visible=True).exclude(handle__in=hide_groups)

    print("Buret: %s\nHoldtutor: %s\nJoker: %s\nAnsvarlig: %s\nAfvist: %s" % (len(buret), len(tutors), len(jokers), len(group_leaders), len(not_tutor)))
    for t in buret:
        groups = ', '.join([g.name for g in group_queryset(t).all()])
        profile = t.profile
        c = Context({
            'webfar': webfar,
            'year': YEAR,
            'navn': profile.name,
            'groups': groups,
            'password': passwords.get(profile.studentnumber),
        })
        e = Email(
            sender=burfar_sender,
            recipient=email(t),
            subject=tpl_buret_subject.render(c),
            body=tpl_buret.render(c),
            kind='buret',
            html=False,
        )
        e.save()

    for t in tutors:
        profile = t.profile
        groups = list(group_queryset(t).all())
        if len(groups) != 2:
            print("Failed to create email for %s: tutor does not have two groups, but %s\n%s\n%s"
                    % (profile.name, unicode(len(groups)), t, groups))
            continue
        group1 = groups[0].name
        group2 = groups[1].name
        c = Context({
            'webfar': webfar,
            'year': YEAR,
            'navn': profile.name,
            'group1': group1,
            'group2': group2,
            'password': passwords.get(profile.studentnumber),
        })
        e = Email(
            sender=webfar_sender,
            recipient=email(t),
            subject=tpl_holdtutor_subject.render(c),
            body=tpl_holdtutor.render(c),
            kind='holdtutor',
            html=True,
        )
        e.save()

    for t in jokers:
        groups = list(group_queryset(t).all())
        if len(groups) != 3:
            print('%s does not have three groups, but %s' % (profile.name, len(groups)))
        group1 = groups[0].name
        group2 = groups[1].name
        group3 = groups[2].name
        profile = t.profile
        c = Context({
            'webfar': webfar,
            'year': YEAR,
            'navn': profile.name,
            'group1': group1,
            'group2': group2,
            'group3': group3,
            'password': passwords.get(profile.studentnumber),
        })
        e = Email(
            sender=webfar_sender,
            recipient=email(t),
            subject=tpl_joker_subject.render(c),
            body=tpl_joker.render(c),
            kind='joker',
            html=True,
        )
        e.save()

    for gl in group_leaders:
        t = gl.tutor
        profile = t.profile
        c = Context({
            'webfar': webfar,
            'year': YEAR,
            'navn': profile.name,
            'group': gl.group.name,
        })
        e = Email(
            sender=webfar_sender,
            recipient=email(t),
            subject=tpl_ansvarlig_subject.render(c),
            body=tpl_ansvarlig.render(c),
            kind='ansvarlig',
            html=False,
        )
        e.save()

    for t in not_tutor:
        c = Context(dict(year=YEAR, **t))
        e = Email(
            sender=best_sender,
            recipient=t['email'],
            subject=tpl_afvist_subject.render(c),
            body=tpl_afvist.render(c),
            kind='afvist',
            html=False,
        )
        e.save()


def __main__():
    rejects = read_rejects()
