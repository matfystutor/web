# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0002_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tutorprofile',
            name='birthday',
        ),
        migrations.RemoveField(
            model_name='tutorprofile',
            name='gender',
        ),
    ]
