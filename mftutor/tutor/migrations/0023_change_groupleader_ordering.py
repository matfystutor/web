# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0022_change_tutorgroup_ordering'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tutorgroupleader',
            options={'ordering': ['group'], 'verbose_name': 'gruppeansvarlig', 'verbose_name_plural': 'gruppeansvarlige'},
        ),
    ]
