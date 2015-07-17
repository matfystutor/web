# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0021_add_related_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tutorgroup',
            options={'ordering': ['-year', 'name', 'handle'], 'verbose_name': 'arbejdsgruppe', 'verbose_name_plural': 'arbejdsgrupper'},
        ),
    ]
