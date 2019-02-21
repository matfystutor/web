# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShirtOption',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('choice', models.CharField(max_length=60)),
                ('position', models.IntegerField()),
            ],
            options={
                'ordering': ('position',),
            },
        ),
        migrations.CreateModel(
            name='ShirtPreference',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('choice1', models.CharField(max_length=60)),
                ('choice2', models.CharField(max_length=60)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('profile', models.ForeignKey(to='tutor.TutorProfile')),
            ],
        ),
    ]
