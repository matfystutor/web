# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('confirmation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='confirmation',
            name='previous_tutor',
            field=models.CharField(max_length=500, verbose_name='Har du tidligere v\xe6ret tutor?', blank=True),
        ),
    ]
