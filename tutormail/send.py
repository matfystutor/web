# vim: set fileencoding=utf-8:
from .models import Email

def get_queryset():
    return Email.objects.filter(sent__exact=None, retain=False, archive=False).order_by('-kind')

def get_one():
    return get_queryset().all()[0]

def make_email_message(mailobj):
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

def delayed_send_all():
    import time
    from datetime import datetime
    emails = get_queryset()
    for email in emails.all():
        print email
        send_messages((make_email_message(email),), email_backend_type)
        email.sent = datetime.now()
        email.save()
        time.sleep(20)

def make_mails():
    from tutor.models import Tutor, TutorGroupLeader
    from mftutor.settings import YEAR

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
    # joker - 20117268 (Diana) og 20117043 (Katrin Debes)
    joker_numbers = ('20117268', '20117043')

    # no mail to Camilla 20103508 or Eske 20103494
    no_mail = ['20103508', '20103494']

    hide_groups = ('alle', 'best', 'buret', 'sponsor')

    all_tutors = Tutor.objects.filter(year=YEAR).exclude(profile__studentnumber__in=no_mail)
    buret = all_tutors.filter(groups__handle='buret').all()
    tutors = all_tutors.exclude(groups__handle='buret').exclude(profile__studentnumber__in=joker_numbers).all()
    group_leaders = list(TutorGroupLeader.objects.filter(year=YEAR).exclude(group__handle__in=hide_groups).all())
    jokers = all_tutors.filter(profile__studentnumber__in=joker_numbers).all()

    from activation.models import ProfileActivation
    not_tutor = ([{'navn': act.profile.get_full_name(), 'email': act.email} for act in ProfileActivation.objects.filter(profile__studentnumber__in=
    (20070001, 20080002,)).all()]
    + [{'navn': u'foo bar', 'email': u'foobar@example.org'},
       {'navn': u'Gordon Freeman', 'email': u'barbaz@example.com'}])

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
    tpl_afvist_subject = Template('Fra tutorgruppen')

    def act_link(tutor):
        try:
            act = ProfileActivation.objects.get(profile__tutor=tutor)
        except ProfileActivation.DoesNotExist:
            return '(din bruger er allerede aktiveret)'
        return 'http://www.matfystutor.dk' + act.get_activation_path()

    def email(tutor):
        if tutor.profile.user:
            return tutor.profile.user.email
        act = ProfileActivation.objects.get(profile__tutor=tutor)
        return act.email

    def group_queryset(tutor):
        return tutor.groups.filter(visible=True).exclude(handle__in=hide_groups)

    for t in buret:
        groups = u', '.join([g.name for g in group_queryset(t).all()])
        profile = t.profile
        c = Context({
            'navn': profile.get_full_name(),
            'activation': act_link(t),
            'groups': groups,
        })
        e = Email(
            sender='Lauge Hoyer <best@matfystutor.dk>',
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
            print profile.get_full_name()+u' does not have two groups, but '+unicode(len(groups))
            print t
            print groups
        group1 = groups[0].name
        group2 = groups[1].name
        c = Context({
            'navn': profile.get_full_name(),
            'activation': act_link(t),
            'group1': group1,
            'group2': group2,
        })
        e = Email(
            sender='Mathias Rav <webfar@matfystutor.dk>',
            recipient=email(t),
            subject=tpl_holdtutor_subject.render(c),
            body=tpl_holdtutor.render(c),
            kind='holdtutor',
            html=True,
        )
        e.save()

    for t in jokers:
        groups = list(group_queryset(t).all())
        if len(groups) != 2:
            print profile.get_full_name()+u' does not have two groups, but '+unicode(len(groups))
        group1 = groups[0].name
        group2 = groups[1].name
        profile = t.profile
        c = Context({
            'navn': profile.get_full_name(),
            'activation': act_link(t),
            'group1': group1,
            'group2': group2,
        })
        e = Email(
            sender='Mathias Rav <webfar@matfystutor.dk>',
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
            'navn': profile.get_full_name(),
            'group': gl.group.name,
        })
        e = Email(
            sender='Mathias Rav <webfar@matfystutor.dk>',
            recipient=email(t),
            subject=tpl_ansvarlig_subject.render(c),
            body=tpl_ansvarlig.render(c),
            kind='ansvarlig',
            html=False,
        )
        e.save()

    for t in not_tutor:
        c = Context(t)
        e = Email(
            sender='"Mat/Fys-Tutorgruppen" <best@matfystutor.dk>',
            recipient=t['email'],
            subject=tpl_afvist_subject.render(c),
            body=tpl_afvist.render(c),
            kind='afvist',
            html=False,
        )
        e.save()

