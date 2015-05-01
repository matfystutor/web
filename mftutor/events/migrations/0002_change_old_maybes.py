# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def remove_maybe(apps, schema_editor):
    EventParticipant = apps.get_model('events', 'EventParticipant')
    for o in EventParticipant.objects.filter(status='maybe'):
        o.status = 'no'
        if o.notes:
            o.notes += ' '
        o.notes += '(was maybe)'
        o.save()


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(remove_maybe)
    ]
