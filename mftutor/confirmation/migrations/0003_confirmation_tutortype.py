# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('confirmation', '0002_confirmation_previous_tutor'),
    ]

    operations = [
        migrations.AddField(
            model_name='confirmation',
            name='tutortype',
            field=models.CharField(max_length=60, verbose_name='Tutor type', blank=True),
        ),
    ]
