# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeLogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='Tidspunkt')),
                ('kind', models.CharField(choices=[('import', 'Import af ruslister'), ('rus_profile', 'Rus: profil ændret'), ('rus_rusclass', 'Rus: rushold ændret'), ('rus_arrived', 'Rus: ankommet ændret'), ('rus_password', 'Rus: kodeord ændret'), ('note_add', 'Notat tilføjet'), ('note_delete', 'Notat slettet'), ('tutor_profile', 'Tutor: profil ændret'), ('tutor_rusclass', 'Tutor: rushold ændret'), ('tutor_password', 'Tutor: kodeord ændret')], max_length=20, verbose_name='Slags')),
                ('payload', models.TextField(blank=True, verbose_name='Beskedparameter')),
                ('related_pk', models.IntegerField()),
                ('serialized_data', models.TextField(blank=True)),
                ('author', models.ForeignKey(to='tutor.TutorProfile', verbose_name='Forfatter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Handout',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('year', models.IntegerField(verbose_name='Tutorår')),
                ('kind', models.CharField(choices=[('note', 'Enkelt bemærkning'), ('subset', 'Tilmelding')], max_length=10, verbose_name='Slags')),
                ('name', models.CharField(max_length=100, verbose_name='Navn')),
                ('note', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Oprettet')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Sidst ændret')),
            ],
            options={
                'verbose_name': 'tilmeldingsliste',
                'verbose_name_plural': 'tilmeldingslister',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HandoutClassResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('note', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Oprettet')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Sidst ændret')),
                ('handout', models.ForeignKey(to='reg.Handout')),
                ('rusclass', models.ForeignKey(to='tutor.RusClass')),
            ],
            options={
                'verbose_name': 'holdbesvarelse',
                'verbose_name_plural': 'holdbesvarelser',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HandoutRusResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('checkmark', models.BooleanField(default=False)),
                ('note', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Oprettet')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Sidst ændret')),
                ('handout', models.ForeignKey(to='reg.Handout')),
                ('rus', models.ForeignKey(to='tutor.Rus')),
            ],
            options={
                'verbose_name': 'rusbesvarelse',
                'verbose_name_plural': 'rusbesvarelser',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImportLine',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('line', models.CharField(max_length=500)),
                ('position', models.IntegerField()),
                ('matched', models.BooleanField(default=False)),
                ('rusclass', models.CharField(blank=True, max_length=500)),
                ('studentnumber', models.CharField(blank=True, max_length=500)),
                ('name', models.CharField(blank=True, max_length=500)),
                ('rus', models.ForeignKey(to='tutor.Rus', null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
                'ordering': ['position'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImportSession',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('year', models.IntegerField(verbose_name='Tutorår')),
                ('name', models.CharField(max_length=200, verbose_name='Navn')),
                ('regex', models.CharField(max_length=500, verbose_name='Regulært udtryk')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Oprettet')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Sidst ændret')),
                ('imported', models.DateTimeField(null=True, blank=True, verbose_name='Importeret')),
                ('author', models.ForeignKey(to='tutor.TutorProfile', verbose_name='Forfatter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LightboxNote',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('year', models.IntegerField(unique=True, verbose_name='Tutorår')),
                ('note', models.TextField(blank=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Sidst ændret')),
                ('color', models.CharField(default='green', choices=[('Grøn', 'green'), ('Gul', 'yellow'), ('Rød', 'red')], max_length=10)),
                ('author', models.ForeignKey(to='tutor.TutorProfile', null=True, verbose_name='Forfatter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LightboxRusClassState',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('color', models.CharField(default='green', choices=[('green', 'Grøn'), ('yellow', 'Gul'), ('red', 'Rød')], max_length=10)),
                ('note', models.TextField(blank=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Sidst ændret')),
                ('author', models.ForeignKey(to='tutor.TutorProfile', null=True, verbose_name='Forfatter')),
                ('rusclass', models.ForeignKey(to='tutor.RusClass', unique=True)),
            ],
            options={
                'verbose_name': 'tavlestatus',
                'ordering': ['rusclass'],
                'verbose_name_plural': 'tavlestatuser',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('subject_kind', models.CharField(choices=[('rus', 'rus'), ('rusclass', 'rusclass'), ('tutor', 'tutor')], max_length=10)),
                ('subject_pk', models.IntegerField()),
                ('body', models.TextField(verbose_name='Note')),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='Tidspunkt')),
                ('deleted', models.DateTimeField(null=True, blank=True, verbose_name='Slettet')),
                ('author', models.ForeignKey(to='tutor.TutorProfile', verbose_name='Forfatter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='importline',
            name='session',
            field=models.ForeignKey(to='reg.ImportSession'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='handoutrusresponse',
            unique_together=set([('handout', 'rus')]),
        ),
        migrations.AlterUniqueTogether(
            name='handoutclassresponse',
            unique_together=set([('handout', 'rusclass')]),
        ),
        migrations.AlterUniqueTogether(
            name='handout',
            unique_together=set([('year', 'name')]),
        ),
    ]
