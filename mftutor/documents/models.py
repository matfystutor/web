# coding: utf-8
from datetime import datetime
from django.db import models
from .. import settings

class ReferaterManager(models.Manager):
    def get_queryset(self):
        return super(ReferaterManager, self).get_queryset().filter(
            type__exact='referater').order_by('-year', '-published')


def Document_upload_to(doc, filename):
    return u'docs/%s/%s/%s' % (doc.year, doc.type, filename)


class Document(models.Model):
    objects = models.Manager()
    referater = ReferaterManager()

    title = models.CharField(
        max_length=100, verbose_name='Titel')
    year = models.IntegerField(
        verbose_name="Tutorår", default=settings.YEAR)
    published = models.DateField(
        verbose_name='Dato')
    time_of_upload = models.DateTimeField(
        editable=False, auto_now_add=True)

    # type_choices must match the regex in urls.py
    type_choices = (
        ("guides", "Guide"),
        ("referater", "Referat"),
        ("udgivelser","Udgivelse"),
    )
    type = models.CharField(
        max_length=30, choices=type_choices, verbose_name="Type")

    doc_file = models.FileField(
        upload_to=Document_upload_to, verbose_name="Dokument")

    class Meta:
        ordering = ("-year","title")

    def __str__(self):
        return '[Document %s: %s]' % (self.type, self.title)

    def __unicode__(self):
        return u'[Document %s: %s]' % (self.type, self.title)

    def get_absolute_url(self):
        return settings.MEDIA_URL + unicode(self.doc_file)
