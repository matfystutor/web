from django.core.mail import EmailMessage
from django.template import Template, Context
from django.template.loader import get_template
from .. import settings

def make_password_reset_message(rus, tutor, password):
    tpl_subject = get_template('emails/rus_password_reset_subject.txt')
    tpl_body = get_template('emails/rus_password_reset.txt')
    c = Context({'rus': rus, 'tutor': tutor, 'password': password})
    msg = EmailMessage(
            subject=tpl_subject.render(c),
            body=tpl_body.render(c),
            from_email=settings.PERSONAL_EMAIL_SENDER,
            to=(rus.email,))
    return msg

def send_messages(messages):
    from django.core.mail import get_connection

    backend_type = 'django.core.mail.backends.smtp.EmailBackend'
    #backend_type = 'django.core.mail.backends.dummy.EmailBackend'

    email_backend = get_connection(backend=backend_type)

    return email_backend.send_messages(messages)

