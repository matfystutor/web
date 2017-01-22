# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0029_tutorprofile_user_null'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rus',
            name='initial_rusclass',
            field=models.ForeignKey(related_name='initial_rus_set', on_delete=django.db.models.deletion.SET_NULL, to='tutor.RusClass', null=True),
        ),
        migrations.AlterField(
            model_name='rus',
            name='rusclass',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='tutor.RusClass', null=True),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='rusclass',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='tutor.RusClass', null=True),
        ),
        migrations.AlterField(
            model_name='tutorgroup',
            name='leader',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Gruppeansvarlig', to='tutor.Tutor', null=True),
        ),
    ]
