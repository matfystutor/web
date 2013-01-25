from django.core.urlresolvers import reverse
from django.db import models
from tutor.models import TutorProfile
from datetime import datetime
from django.core.mail import send_mail as django_send_mail
from django.core.mail import EmailMessage
import hashlib

class ProfileActivation(models.Model):
    profile = models.ForeignKey(TutorProfile, unique=True, related_name='activation')
    email = models.EmailField(verbose_name="E-mailadresse til aktivering")
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    activation_key = models.CharField(max_length=40, blank=True, null=True)
    activation_request_time = models.DateTimeField(blank=True, null=True)

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def generate_new_key(self):
        self.activation_request_time = datetime.now()
        self.activation_key = hashlib.sha1(repr(self)).hexdigest()
        self.save()

    def generate_mail(self, domain):
        path = reverse('activate', args=(self.activation_key,))
        link = 'http://' + domain + path
        from django.template.loader import render_to_string
        data = {
            'full_name': self.get_full_name(),
            'link': link,
        }
        body = render_to_string('activation_mail.txt', data)
        msg = EmailMessage(
                subject="Aktiver tutorkonto",
                body=body,
                from_email='Mat/Fys Tutorgruppen <webfar@'+domain+'>',
                to=(self.email,))
        return msg

    def __repr__(self):
        return (unicode(self.profile.pk) + '#' +
                unicode(self.email) + '#' +
                unicode(self.first_name) + '#' +
                unicode(self.last_name) + '#' +
                unicode(self.activation_key) + '#' +
                unicode(self.activation_request_time) + '#' +
                '')
