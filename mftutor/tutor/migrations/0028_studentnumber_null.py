# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0027_remove_tutorgroupleader'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorprofile',
            name='studentnumber',
            field=models.CharField(max_length=20, unique=True, null=True, verbose_name='\xc5rskortnummer', blank=True),
        ),
    ]
