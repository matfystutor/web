# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reg', '0002_rusclass_onetoone'),
    ]

    operations = [
        migrations.AddField(
            model_name='handoutclassresponse',
            name='color',
            field=models.CharField(default='green', max_length=10, choices=[('green', 'Gr\xf8n'), ('yellow', 'Gul'), ('red', 'R\xf8d')]),
        ),
    ]
