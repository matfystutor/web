# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0004_tutorgroup_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorgroup',
            name='fake_id',
            field=models.IntegerField(null=True),
        ),
    ]
