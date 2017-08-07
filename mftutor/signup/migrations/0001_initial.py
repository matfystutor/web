# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0029_tutorprofile_user_null'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(verbose_name='Tutor\xe5r')),
                ('name', models.CharField(max_length=60)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=75)),
                ('studentnumber', models.CharField(max_length=20)),
                ('study', models.CharField(max_length=60)),
                ('previous_tutor_years', models.IntegerField()),
                ('rus_year', models.IntegerField()),
                ('new_password', models.BooleanField()),
                ('accepted', models.BooleanField(default=True)),
                ('buret', models.BooleanField()),
                ('comments', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TutorApplicationGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('priority', models.IntegerField()),
                ('application', models.ForeignKey(to='signup.TutorApplication')),
                ('group', models.ForeignKey(to='tutor.TutorGroup')),
            ],
        ),
        migrations.AddField(
            model_name='tutorapplication',
            name='groups',
            field=models.ManyToManyField(to='tutor.TutorGroup', through='signup.TutorApplicationGroup'),
        ),
        migrations.AddField(
            model_name='tutorapplication',
            name='profile',
            field=models.ForeignKey(blank=True, to='tutor.TutorProfile', null=True),
        ),
    ]
