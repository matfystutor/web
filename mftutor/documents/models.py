# -*- coding: utf-8 -*-

import os
import re
import unicodedata


from django.db import models

from mftutor import settings

class ReferaterManager(models.Manager):
    def get_queryset(self):
        return super(ReferaterManager, self).get_queryset().filter(
            type__exact='referater').order_by('-year', '-published')


TRANSLITERATION = {'æ': 'ae', 'ø': 'oe', 'å': 'aa',
                   'Æ': 'AE', 'Ø': 'OE', 'Å': 'AA'}

def safe_filename(filename):
    """Make an uploaded filename safe to use in an URL

    Danish letters are transliterated, other accents are stripped.
    Any remaining character that is not a letter, digit, dot, underscore or dash
    (for examples spaces) is replaced with an underscore.
    """

    filename = unicodedata.normalize('NFC', os.path.basename(filename))
    name, ext = os.path.splitext(filename)
    for char, replacement in TRANSLITERATION.items():
        name = name.replace(char, replacement)
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    name = re.sub(r'[^A-Za-z0-9._-]+', '_', name).strip('._') or 'dokument'
    ext = re.sub(r'[^A-Za-z0-9.]', '', ext.lower())
    return name + ext



def Document_upload_to(doc, filename):
    return 'docs/%s/%s/%s' % (doc.year, doc.type, safe_filename(filename))


class Document(models.Model):
    objects = models.Manager()
    referater = ReferaterManager()

    title = models.CharField(
        max_length=100, verbose_name='Titel')
    year = models.IntegerField(
        verbose_name="Tutorår")
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

    def get_absolute_url(self):
        return self.doc_file.url 
