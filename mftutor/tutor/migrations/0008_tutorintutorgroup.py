# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0007_auto_20150708_1257'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorInTutorGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tutor', models.ForeignKey(to='tutor.Tutor')),
                ('tutorgroup', models.ForeignKey(to='tutor.TutorGroup', to_field='fake_id')),
            ],
        ),
    ]
