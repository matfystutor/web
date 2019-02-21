# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import mftutor.tutor


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BoardMember',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('position', models.IntegerField(verbose_name='Rækkefølge')),
                ('title', models.CharField(max_length=50, verbose_name='Titel')),
            ],
            options={
                'ordering': ['tutor__year', 'position'],
                'verbose_name_plural': 'bestyrelsesmedlemmer',
                'verbose_name': 'bestyrelsesmedlem',
            },
        ),
        migrations.CreateModel(
            name='Rus',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('year', models.IntegerField(verbose_name='Tutorår')),
                ('arrived', models.BooleanField(default=False, verbose_name='Ankommet')),
            ],
            options={
                'ordering': ['rusclass', 'profile'],
                'verbose_name_plural': 'russer',
                'verbose_name': 'rus',
            },
        ),
        migrations.CreateModel(
            name='RusClass',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('official_name', models.CharField(max_length=20, help_text='DA1, MØ3, osv.', verbose_name='AU-navn')),
                ('internal_name', models.CharField(max_length=20, help_text='Dat1, Møk3, osv.', verbose_name='Internt navn')),
                ('handle', models.CharField(max_length=20, help_text='dat1, mok3, osv. Bruges i holdets emailadresse', verbose_name='Email')),
                ('year', models.IntegerField(verbose_name='Tutorår')),
            ],
            options={
                'ordering': ['year', 'internal_name'],
                'verbose_name_plural': 'rushold',
                'verbose_name': 'rushold',
            },
        ),
        migrations.CreateModel(
            name='Tutor',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('year', models.IntegerField(verbose_name='Tutorår')),
                ('early_termination', models.DateTimeField(help_text='Tidspunkt i året hvor tutoren stopper i foreningen', null=True, blank=True, verbose_name='Ekskluderet')),
                ('early_termination_reason', models.TextField(help_text='Årsag til at tutoren stopper', null=True, blank=True, verbose_name='Eksklusionsårsag')),
            ],
            options={
                'ordering': ['-year'],
                'verbose_name_plural': 'tutorer',
                'verbose_name': 'tutor',
            },
        ),
        migrations.CreateModel(
            name='TutorGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('handle', models.CharField(max_length=20, help_text='Bruges i gruppens emailadresse', verbose_name='Kort navn')),
                ('name', models.CharField(max_length=40, help_text='Vises på hjemmesiden', verbose_name='Langt navn')),
                ('visible', models.BooleanField(default=False)),
                ('year', models.IntegerField(null=True, verbose_name='Tutorår')),
                ('leader', models.ForeignKey(to='tutor.Tutor', blank=True, verbose_name='Gruppeansvarlig', on_delete=django.db.models.deletion.SET_NULL, null=True)),
            ],
            options={
                'ordering': ['-year', 'name', 'handle'],
                'verbose_name_plural': 'arbejdsgrupper',
                'verbose_name': 'arbejdsgruppe',
            },
        ),
        migrations.CreateModel(
            name='TutorInTutorGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tutor', models.ForeignKey(to='tutor.Tutor')),
                ('tutorgroup', models.ForeignKey(to='tutor.TutorGroup')),
            ],
        ),
        migrations.CreateModel(
            name='TutorProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=60, verbose_name='Fulde navn')),
                ('street', models.CharField(max_length=80, blank=True, verbose_name='Adresse')),
                ('city', models.CharField(max_length=40, blank=True, verbose_name='Postnr. og by')),
                ('phone', models.CharField(max_length=20, blank=True, verbose_name='Telefonnr.')),
                ('email', models.EmailField(max_length=75, verbose_name='E-mailadresse')),
                ('study', models.CharField(max_length=60, blank=True, verbose_name='Studieretning')),
                ('studentnumber', models.CharField(max_length=20, null=True, blank=True, unique=True, verbose_name='Årskortnummer')),
                ('picture', models.ImageField(upload_to=mftutor.tutor.tutorpicture_upload_to, blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True)),
            ],
            options={
                'verbose_name_plural': 'tutorprofiler',
                'verbose_name': 'tutorprofil',
            },
        ),
        migrations.AddField(
            model_name='tutor',
            name='groups',
            field=models.ManyToManyField(to='tutor.TutorGroup', blank=True, verbose_name='Arbejdsgrupper'),
        ),
        migrations.AddField(
            model_name='tutor',
            name='profile',
            field=models.ForeignKey(to='tutor.TutorProfile'),
        ),
        migrations.AddField(
            model_name='tutor',
            name='rusclass',
            field=models.ForeignKey(to='tutor.RusClass', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='rus',
            name='initial_rusclass',
            field=models.ForeignKey(to='tutor.RusClass', on_delete=django.db.models.deletion.SET_NULL, related_name='initial_rus_set', null=True),
        ),
        migrations.AddField(
            model_name='rus',
            name='profile',
            field=models.ForeignKey(to='tutor.TutorProfile'),
        ),
        migrations.AddField(
            model_name='rus',
            name='rusclass',
            field=models.ForeignKey(to='tutor.RusClass', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='boardmember',
            name='tutor',
            field=models.ForeignKey(to='tutor.Tutor'),
        ),
        migrations.AlterUniqueTogether(
            name='tutor',
            unique_together=set([('profile', 'year')]),
        ),
    ]
