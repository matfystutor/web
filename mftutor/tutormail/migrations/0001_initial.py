# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=100, blank=True, verbose_name='Fra')),
                ('recipient', models.CharField(max_length=100, blank=True, verbose_name='Til')),
                ('subject', models.CharField(max_length=100, blank=True, verbose_name='Emne')),
                ('body', models.TextField(blank=True, verbose_name='Tekst')),
                ('kind', models.CharField(max_length=100, blank=True, verbose_name='Slags')),
                ('sent', models.DateTimeField(null=True, blank=True, verbose_name='Sendt')),
                ('retain', models.BooleanField(default=False, verbose_name='Tilbagehold')),
                ('manually_changed', models.DateTimeField(null=True, blank=True, verbose_name='Ændret manuelt')),
                ('archive', models.BooleanField(default=False, verbose_name='Arkiveret')),
                ('html', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['kind', 'recipient', 'pk'],
            },
        ),
    ]
