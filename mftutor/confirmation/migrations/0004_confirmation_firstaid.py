# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('confirmation', '0003_confirmation_tutortype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmation',
            name='firstaid',
            field=models.CharField(max_length=500, verbose_name='F\xf8rstehj\xe6lpskursus', blank=True),
        ),
    ]
