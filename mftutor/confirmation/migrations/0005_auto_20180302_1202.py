# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('confirmation', '0004_confirmation_firstaid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmation',
            name=b'firstaid',
            field=models.CharField(max_length=500, verbose_name=b'F\xc3\xb8rstehj\xc3\xa6lpskursus', blank=True),
        ),
        migrations.AlterField(
            model_name='confirmation',
            name=b'previous_tutor',
            field=models.CharField(max_length=500, verbose_name=b'Har du tidligere v\xc3\xa6ret tutor?', blank=True),
        ),
    ]
