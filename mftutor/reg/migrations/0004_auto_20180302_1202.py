# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reg', '0003_handoutclassresponse_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='handoutclassresponse',
            name=b'color',
            field=models.CharField(default=b'green', max_length=10, choices=[(b'green', b'Gr\xc3\xb8n'), (b'yellow', b'Gul'), (b'red', b'R\xc3\xb8d')]),
        ),
    ]
