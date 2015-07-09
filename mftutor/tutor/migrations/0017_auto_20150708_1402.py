# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0016_auto_20150708_1402'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorgroupleader',
            name='group',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='tutorintutorgroup',
            name='tutorgroup',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='tutorgroup',
            name='id',
            field=models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True),
        ),
        migrations.AlterField(
            model_name='tutorgroupleader',
            name='group',
            field=models.ForeignKey(related_name='+', to='tutor.TutorGroup'),
        ),
        migrations.AlterField(
            model_name='tutorintutorgroup',
            name='tutorgroup',
            field=models.ForeignKey(to='tutor.TutorGroup'),
        ),
    ]
