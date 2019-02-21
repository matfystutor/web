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
            name='ChangeLogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='Tidspunkt')),
                ('kind', models.CharField(max_length=20, choices=[('import', 'Import af ruslister'), ('rus_profile', 'Rus: profil ændret'), ('rus_rusclass', 'Rus: rushold ændret'), ('rus_arrived', 'Rus: ankommet ændret'), ('rus_password', 'Rus: kodeord ændret'), ('note_add', 'Notat tilføjet'), ('note_delete', 'Notat slettet'), ('tutor_profile', 'Tutor: profil ændret'), ('tutor_rusclass', 'Tutor: rushold ændret'), ('tutor_password', 'Tutor: kodeord ændret')], verbose_name='Slags')),
                ('payload', models.TextField(blank=True, verbose_name='Beskedparameter')),
                ('related_pk', models.IntegerField()),
                ('serialized_data', models.TextField(blank=True)),
                ('author', models.ForeignKey(to='tutor.TutorProfile', verbose_name='Forfatter')),
            ],
        ),
        migrations.CreateModel(
            name='Handout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(verbose_name='Tutorår')),
                ('kind', models.CharField(max_length=10, choices=[('note', 'Enkelt bemærkning'), ('subset', 'Tilmelding')], verbose_name='Slags')),
                ('name', models.CharField(max_length=100, verbose_name='Navn')),
                ('note', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Oprettet')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Sidst ændret')),
            ],
            options={
                'verbose_name_plural': 'tilmeldingslister',
                'verbose_name': 'tilmeldingsliste',
            },
        ),
        migrations.CreateModel(
            name='HandoutClassResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=10, choices=[('green', 'Grøn'), ('yellow', 'Gul'), ('red', 'Rød')], default='green')),
                ('note', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Oprettet')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Sidst ændret')),
                ('handout', models.ForeignKey(to='reg.Handout')),
                ('rusclass', models.ForeignKey(to='tutor.RusClass')),
            ],
            options={
                'verbose_name_plural': 'holdbesvarelser',
                'verbose_name': 'holdbesvarelse',
            },
        ),
        migrations.CreateModel(
            name='HandoutRusResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checkmark', models.BooleanField(default=False)),
                ('note', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Oprettet')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Sidst ændret')),
                ('handout', models.ForeignKey(to='reg.Handout')),
                ('rus', models.ForeignKey(to='tutor.Rus')),
            ],
            options={
                'verbose_name_plural': 'rusbesvarelser',
                'verbose_name': 'rusbesvarelse',
            },
        ),
        migrations.CreateModel(
            name='ImportLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line', models.CharField(max_length=500)),
                ('position', models.IntegerField()),
                ('matched', models.BooleanField(default=False)),
                ('rusclass', models.CharField(max_length=500, blank=True)),
                ('studentnumber', models.CharField(max_length=500, blank=True)),
                ('name', models.CharField(max_length=500, blank=True)),
                ('rus', models.ForeignKey(to='tutor.Rus', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True)),
            ],
            options={
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='ImportSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(verbose_name='Tutorår')),
                ('name', models.CharField(max_length=200, verbose_name='Navn')),
                ('regex', models.CharField(max_length=500, verbose_name='Regulært udtryk')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Oprettet')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Sidst ændret')),
                ('imported', models.DateTimeField(null=True, blank=True, verbose_name='Importeret')),
                ('author', models.ForeignKey(to='tutor.TutorProfile', verbose_name='Forfatter')),
            ],
        ),
        migrations.CreateModel(
            name='LightboxNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(unique=True, verbose_name='Tutorår')),
                ('note', models.TextField(blank=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Sidst ændret')),
                ('color', models.CharField(max_length=10, choices=[('Grøn', 'green'), ('Gul', 'yellow'), ('Rød', 'red')], default='green')),
                ('author', models.ForeignKey(to='tutor.TutorProfile', verbose_name='Forfatter', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LightboxRusClassState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=10, choices=[('green', 'Grøn'), ('yellow', 'Gul'), ('red', 'Rød')], default='green')),
                ('note', models.TextField(blank=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Sidst ændret')),
                ('author', models.ForeignKey(to='tutor.TutorProfile', verbose_name='Forfatter', null=True)),
                ('rusclass', models.OneToOneField(to='tutor.RusClass')),
            ],
            options={
                'ordering': ['rusclass'],
                'verbose_name_plural': 'tavlestatuser',
                'verbose_name': 'tavlestatus',
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject_kind', models.CharField(max_length=10, choices=[('rus', 'rus'), ('rusclass', 'rusclass'), ('tutor', 'tutor')])),
                ('subject_pk', models.IntegerField()),
                ('body', models.TextField(verbose_name='Note')),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='Tidspunkt')),
                ('deleted', models.DateTimeField(null=True, blank=True, verbose_name='Slettet')),
                ('author', models.ForeignKey(to='tutor.TutorProfile', verbose_name='Forfatter')),
            ],
        ),
        migrations.AddField(
            model_name='importline',
            name='session',
            field=models.ForeignKey(to='reg.ImportSession'),
        ),
        migrations.AlterUniqueTogether(
            name='handout',
            unique_together=set([('year', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='handoutrusresponse',
            unique_together=set([('handout', 'rus')]),
        ),
        migrations.AlterUniqueTogether(
            name='handoutclassresponse',
            unique_together=set([('handout', 'rusclass')]),
        ),
    ]
