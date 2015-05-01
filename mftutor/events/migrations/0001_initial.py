# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('rsvp', models.DateTimeField(blank=True, null=True, verbose_name='Tilmeldingsfrist')),
            ],
            options={
                'ordering': ['start_date', 'start_time'],
                'verbose_name_plural': 'begivenheder',
                'verbose_name': 'begivenhed',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventParticipant',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('status', models.CharField(choices=[('yes', 'Kommer'), ('no', 'Kommer ikke'), ('maybe', 'Har ikke taget stilling')], max_length=10, verbose_name='Tilbagemelding')),
                ('notes', models.TextField(blank=True)),
                ('event', models.ForeignKey(to='events.Event', related_name='participants')),
                ('tutor', models.ForeignKey(to='tutor.Tutor', related_name='events')),
            ],
            options={
                'ordering': ['event', 'status'],
                'verbose_name_plural': 'tilbagemeldinger',
                'verbose_name': 'tilbagemelding',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='eventparticipant',
            unique_together=set([('event', 'tutor')]),
        ),
    ]
