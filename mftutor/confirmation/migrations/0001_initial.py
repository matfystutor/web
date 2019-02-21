# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Confirmation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('study', models.CharField(max_length=500, blank=True, verbose_name='Studium samt sidefag/tilvalg')),
                ('tutortype', models.CharField(max_length=60, blank=True, verbose_name='Tutor type')),
                ('experience', models.CharField(max_length=60, blank=True, verbose_name='Tidligere erfaring som holdtutor')),
                ('resits', models.CharField(max_length=500, blank=True, verbose_name='Reeksamener i rusugen')),
                ('priorities', models.CharField(max_length=60, blank=True, verbose_name='Ønskede studieretninger')),
                ('firstaid', models.CharField(max_length=500, blank=True, verbose_name='Førstehjælpskursus')),
                ('rusfriends', models.CharField(max_length=500, blank=True, verbose_name='Bekendte nye studerende')),
                ('comment', models.CharField(max_length=500, blank=True, verbose_name='Kommentar')),
                ('previous_tutor', models.CharField(max_length=500, blank=True, verbose_name='Har du tidligere været tutor?')),
                ('internal_notes', models.CharField(max_length=500, blank=True, verbose_name='Notat')),
                ('tutor', models.OneToOneField(to='tutor.Tutor', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('tutor',),
            },
        ),
    ]
