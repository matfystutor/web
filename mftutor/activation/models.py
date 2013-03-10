import hashlib
from datetime import datetime

from django.core.urlresolvers import reverse
from django.db import models
from django.core.mail import send_mail as django_send_mail
from django.core.mail import EmailMessage

from ..settings import YEAR
from ..tutor.models import TutorProfile, Tutor

class ProfileActivation(models.Model):
    profile = models.OneToOneField(TutorProfile, null=True, blank=True, related_name='activation')
    email = models.EmailField(verbose_name="E-mailadresse til aktivering")
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    activation_key = models.CharField(max_length=40, blank=True, null=True)
    activation_request_time = models.DateTimeField(blank=True, null=True)

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def generate_new_key(self):
        self.activation_request_time = datetime.now()
        signature = repr(self)
        self.activation_key = hashlib.sha1(signature).hexdigest()
        self.save()

    def get_activation_path(self):
        if not self.activation_key:
            self.generate_new_key()
        key = self.activation_key
        return reverse('activate', kwargs={'activation_key': key})

    def generate_mail(self, domain, template=None, title_template=None):
        if template is None:
            from django.template.loader import get_template
            template = get_template('activation_mail.txt')
        if title_template is None:
            from django.template import Template
            title_template = Template("Aktiver tutorkonto")
        path = self.get_activation_path()
        link = 'http://' + domain + path

        try:
            groups = [group.name for group in Tutor.objects.get(
                    profile=self.profile,
                    year__exact=YEAR,
                ).groups.filter(
                    visible=True,
                ).exclude(
                    handle__exact='alle'
                ).all()]
        except Tutor.DoesNotExist:
            groups = []

        data = {
            'full_name': self.get_full_name(),
            'year': YEAR,
            'link': link,
            'groups': groups,
        }
        from django.template import Context
        context = Context(data)
        body = template.render(context)
        msg = EmailMessage(
                subject="Aktiver tutorkonto",
                body=body,
                from_email='Mat/Fys Tutorgruppen <webfar@'+domain+'>',
                to=(self.email,))
        return msg

    def __repr__(self):
        activation_data = u''
        if self.activation_request_time:
            activation_data += unicode(self.activation_request_time) + u'#'
        if self.activation_key:
            activation_data += unicode(self.activation_key) + u'#'
        return (unicode(self.profile.pk) + u'#' +
                (self.email) + u'#' +
                (self.first_name) + u'#' +
                (self.last_name) + u'#' +
                activation_data +
                u'').encode('ascii', 'ignore')
