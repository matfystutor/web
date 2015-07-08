# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0006_auto_20150708_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorgroup',
            name='fake_id',
            field=models.IntegerField(unique=True),
        ),
    ]
