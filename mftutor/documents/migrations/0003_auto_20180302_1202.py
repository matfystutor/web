# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_remove_year_default'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name=b'year',
            field=models.IntegerField(verbose_name=b'Tutor\xc3\xa5r'),
        ),
    ]
