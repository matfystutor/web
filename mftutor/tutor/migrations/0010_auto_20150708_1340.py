# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0009_auto_20150708_1300'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tutor',
            name='groups',
        ),
        migrations.AddField(
            model_name='tutor',
            name='groups',
            field=models.ManyToManyField(to='tutor.TutorGroup', verbose_name='Arbejdsgrupper', through='tutor.TutorInTutorGroup', blank=True),
        ),
    ]
