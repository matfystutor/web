# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_event_rsvp_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='rsvp_title',
            field=models.CharField(max_length=200, verbose_name=b'Titel p\xc3\xa5 tilmelding', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='rsvp_description',
            field=models.TextField(verbose_name=b'Noter til tilmelding', blank=True),
        ),
        migrations.AlterField(
            model_name='eventparticipant',
            name=b'notes',
            field=models.TextField(verbose_name=b'Noter', blank=True),
        ),
        migrations.AlterField(
            model_name='eventparticipant',
            name=b'status',
            field=models.CharField(max_length=10, verbose_name=b'Svar', choices=[(b'yes', b'Kommer'), (b'no', b'Kommer ikke')]),
        ),
    ]
