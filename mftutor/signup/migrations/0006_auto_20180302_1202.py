# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signup', '0005_auto_20170206_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailtemplate',
            name=b'year',
            field=models.IntegerField(verbose_name=b'Tutor\xc3\xa5r'),
        ),
        migrations.AlterField(
            model_name='tutorapplication',
            name=b'year',
            field=models.IntegerField(verbose_name=b'Tutor\xc3\xa5r'),
        ),
    ]
