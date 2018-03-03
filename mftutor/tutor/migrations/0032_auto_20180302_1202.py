# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0031_auto_20170216_1447'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorgroup',
            name=b'year',
            field=models.IntegerField(null=True, verbose_name=b'Tutor\xc3\xa5r'),
        ),
        migrations.AlterField(
            model_name='tutorprofile',
            name=b'studentnumber',
            field=models.CharField(max_length=20, unique=True, null=True, verbose_name=b'\xc3\x85rskortnummer', blank=True),
        ),
    ]
