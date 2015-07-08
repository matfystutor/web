# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0014_group_not_null'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorgroup',
            name='fake_id',
            field=models.IntegerField(serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='tutorgroup',
            name='handle',
            field=models.CharField(help_text='Bruges i gruppens emailadresse', max_length=20, verbose_name='Kort navn'),
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
