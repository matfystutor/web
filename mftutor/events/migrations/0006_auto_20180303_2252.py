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
            field=models.CharField(verbose_name='Titel på tilmelding', max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='rsvp_description',
            field=models.TextField(verbose_name='Noter til tilmelding', blank=True),
        ),
        migrations.AlterField(
            model_name='eventparticipant',
            name='notes',
            field=models.TextField(verbose_name='Noter', blank=True),
        ),
        migrations.AlterField(
            model_name='eventparticipant',
            name='status',
            field=models.CharField(verbose_name='Svar', max_length=10, choices=[('yes', 'Kommer'), ('no', 'Kommer ikke')]),
        ),
    ]
