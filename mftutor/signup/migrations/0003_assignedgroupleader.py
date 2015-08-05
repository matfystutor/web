# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0029_tutorprofile_user_null'),
        ('signup', '0002_add_ordering_add_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignedGroupLeader',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('application', models.ForeignKey(to='signup.TutorApplication')),
                ('group', models.OneToOneField(to='tutor.TutorGroup')),
            ],
        ),
    ]
