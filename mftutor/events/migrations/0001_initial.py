# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('location', models.CharField(max_length=200, blank=True)),
                ('description', models.TextField(blank=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('start_time', models.TimeField(null=True, blank=True)),
                ('end_time', models.TimeField(null=True, blank=True)),
                ('rsvp', models.DateTimeField(null=True, blank=True, verbose_name='Tilmeldingsfrist')),
                ('rsvp_title', models.CharField(max_length=200, blank=True, verbose_name='Titel på tilmelding')),
                ('rsvp_description', models.TextField(blank=True, verbose_name='Noter til tilmelding')),
            ],
            options={
                'ordering': ['start_date', 'start_time'],
                'verbose_name_plural': 'begivenheder',
                'verbose_name': 'begivenhed',
            },
        ),
        migrations.CreateModel(
            name='EventParticipant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=10, choices=[('yes', 'Kommer'), ('no', 'Kommer ikke')], verbose_name='Svar')),
                ('notes', models.TextField(blank=True, verbose_name='Noter')),
                ('event', models.ForeignKey(related_name='participants', to='events.Event')),
                ('tutor', models.ForeignKey(related_name='events', to='tutor.Tutor')),
            ],
            options={
                'ordering': ['event', 'status'],
                'verbose_name_plural': 'tilbagemeldinger',
                'verbose_name': 'tilbagemelding',
            },
        ),
        migrations.AlterUniqueTogether(
            name='eventparticipant',
            unique_together=set([('event', 'tutor')]),
        ),
    ]
