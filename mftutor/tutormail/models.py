# vim:set fileencoding=utf-8 :
from django.db import models

#Modelfelter: fra, til, emne, tekst, slags, sendt?, tilbagehold, ændret manuelt, arkiveret
class Email(models.Model):
    sender = models.CharField(blank=True, max_length=100, verbose_name='Fra')
    recipient = models.CharField(blank=True, max_length=100, verbose_name='Til')
    subject = models.CharField(blank=True, max_length=100, verbose_name='Emne')
    body = models.TextField(blank=True, verbose_name='Tekst')
    kind = models.CharField(blank=True, max_length=100, verbose_name='Slags')
    sent = models.DateTimeField(blank=True, null=True, verbose_name='Sendt')
    retain = models.BooleanField(verbose_name='Tilbagehold', default=False)
    manually_changed = models.DateTimeField(blank=True, null=True, verbose_name='Ændret manuelt')
    archive = models.BooleanField(verbose_name='Arkiveret', default=False)
    html = models.BooleanField(default=False)

    class Meta:
        ordering = ['kind', 'recipient', 'pk']

    def __str__(self):
        return 'Email to "%s" kind "%s" subject "%s"' % (
            self.recipient,
            self.kind,
            self.subject,
        )

    def __unicode__(self):
        return u"Email to \"" + self.recipient + u"\" kind \"" + self.kind + u"\" subject \"" + self.subject + u"\""
