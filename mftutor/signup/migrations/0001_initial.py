# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignedGroupLeader',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(verbose_name='Tutorår')),
                ('text', models.TextField()),
                ('subject', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='TutorApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(verbose_name='Tutorår')),
                ('name', models.CharField(max_length=60)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=75)),
                ('studentnumber', models.CharField(max_length=20)),
                ('study', models.CharField(max_length=60)),
                ('previous_tutor_years', models.IntegerField()),
                ('rus_year', models.IntegerField()),
                ('new_password', models.BooleanField()),
                ('accepted', models.BooleanField(default=True)),
                ('tutortype', models.CharField(max_length=20)),
                ('comments', models.TextField(blank=True)),
                ('assigned_groups', models.ManyToManyField(related_name='tutorapplication_assigned_set', to='tutor.TutorGroup')),
                ('email_template', models.ForeignKey(to='signup.EmailTemplate', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TutorApplicationGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.IntegerField()),
                ('application', models.ForeignKey(to='signup.TutorApplication', on_delete=models.CASCADE)),
                ('group', models.ForeignKey(to='tutor.TutorGroup', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('priority',),
            },
        ),
        migrations.AddField(
            model_name='tutorapplication',
            name='groups',
            field=models.ManyToManyField(through='signup.TutorApplicationGroup', to='tutor.TutorGroup'),
        ),
        migrations.AddField(
            model_name='tutorapplication',
            name='profile',
            field=models.ForeignKey(to='tutor.TutorProfile', blank=True, null=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='assignedgroupleader',
            name='application',
            field=models.ForeignKey(to='signup.TutorApplication', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='assignedgroupleader',
            name='group',
            field=models.OneToOneField(to='tutor.TutorGroup', on_delete=models.CASCADE),
        ),
    ]
