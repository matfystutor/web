# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0017_auto_20150708_1402'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutor',
            name='groups2',
            field=models.ManyToManyField(related_name='+', verbose_name='Arbejdsgrupper', to='tutor.TutorGroup', blank=True),
        ),
    ]
