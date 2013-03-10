# vim:set fileencoding=utf-8:
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'mftutor.settings'

from activation.models import ProfileActivation
from mftutor import settings
from django.template import Template

email_backend_type = 'django.core.mail.backends.console.EmailBackend'

def send_messages(messages, backend_type):
    from django.core.mail import get_connection

    email_backend = get_connection(backend=backend_type)

    return email_backend.send_messages(messages)

subject = Template("Du er blevet tutor")

template = Template("""
Hej {{ full_name }},

Tillykke *konfetti*

Du er blevet tutor i {{ year }} og er blevet medlem af grupperne:

{% for group in groups %}{{ group }}
{% endfor %}
Du skal nu gå ind på hjemmesiden og vælge et kodeord.
Det gør du ved følgende link:

{{ link }}

Du skal uploade et billede af dig selv og angive dine kontaktoplysninger.
Det gør du under menuen "Personligt" når du er logget ind.

Hvis du har spørgsmål eller problemer, kan du kontakte
tutorgruppens bestyrelse <best@matfystutor.dk>, eller skrive
direkte til den webansvarlige <webfar@matfystutor.dk>.

Med venlig hilsen
Mat/Fys-Tutorgruppen
""")
msgs = [act.generate_mail(
        domain="matfystutor.dk",
        template=template,
        title_template=subject) for act in 
        ProfileActivation.objects.filter(profile__tutor__year__exact=2013).all()]
send_messages(msgs, email_backend_type)
