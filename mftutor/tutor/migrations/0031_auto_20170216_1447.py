# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0030_auto_20150805_1658'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorgroup',
            name='leader',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Gruppeansvarlig', blank=True, to='tutor.Tutor', null=True),
        ),
    ]
