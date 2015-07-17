# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0023_change_groupleader_ordering'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tutorgroupleader',
            name='year',
        ),
    ]
