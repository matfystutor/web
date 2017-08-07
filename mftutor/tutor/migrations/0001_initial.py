# -*- coding: utf-8 -*-


from django.db import models, migrations
import mftutor.tutor.models
from django.conf import settings


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
                'verbose_name_plural': 'bestyrelsesmedlemmer',
                'ordering': ['tutor__year', 'position'],
                'verbose_name': 'bestyrelsesmedlem',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rus',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('year', models.IntegerField(verbose_name='Tutorår')),
                ('arrived', models.BooleanField(default=False, verbose_name='Ankommet')),
            ],
            options={
                'verbose_name_plural': 'russer',
                'ordering': ['rusclass', 'profile'],
                'verbose_name': 'rus',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RusClass',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('official_name', models.CharField(help_text='DA1, MØ3, osv.', max_length=20, verbose_name='AU-navn')),
                ('internal_name', models.CharField(help_text='Dat1, Møk3, osv.', max_length=20, verbose_name='Internt navn')),
                ('handle', models.CharField(help_text='dat1, mok3, osv. Bruges i holdets emailadresse', max_length=20, verbose_name='Email')),
                ('year', models.IntegerField(verbose_name='Tutorår')),
            ],
            options={
                'verbose_name_plural': 'rushold',
                'ordering': ['year', 'internal_name'],
                'verbose_name': 'rushold',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tutor',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('year', models.IntegerField(verbose_name='Tutorår')),
                ('early_termination', models.DateTimeField(null=True, blank=True, help_text='Tidspunkt i året hvor tutoren stopper i foreningen', verbose_name='Ekskluderet')),
                ('early_termination_reason', models.TextField(null=True, blank=True, help_text='Årsag til at tutoren stopper', verbose_name='Eksklusionsårsag')),
            ],
            options={
                'verbose_name_plural': 'tutorer',
                'ordering': ['-year'],
                'verbose_name': 'tutor',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TutorGroup',
            fields=[
                ('handle', models.CharField(verbose_name='Kort navn', serialize=False, help_text='Bruges i gruppens emailadresse', max_length=20, primary_key=True)),
                ('name', models.CharField(help_text='Vises på hjemmesiden', max_length=40, verbose_name='Langt navn')),
                ('visible', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'arbejdsgrupper',
                'ordering': ['name', 'handle'],
                'verbose_name': 'arbejdsgruppe',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TutorGroupLeader',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('year', models.IntegerField()),
                ('group', models.ForeignKey(to='tutor.TutorGroup')),
                ('tutor', models.ForeignKey(to='tutor.Tutor')),
            ],
            options={
                'verbose_name_plural': 'gruppeansvarlige',
                'ordering': ['-year', 'group'],
                'verbose_name': 'gruppeansvarlig',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TutorProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=60, verbose_name='Fulde navn')),
                ('street', models.CharField(blank=True, max_length=80, verbose_name='Adresse')),
                ('city', models.CharField(blank=True, max_length=40, verbose_name='Postnr. og by')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Telefonnr.')),
                ('email', models.EmailField(max_length=75, verbose_name='E-mailadresse')),
                ('birthday', models.DateField(null=True, blank=True, verbose_name='Født')),
                ('study', models.CharField(blank=True, max_length=60, verbose_name='Studieretning')),
                ('studentnumber', models.CharField(unique=True, max_length=20, verbose_name='Årskortnummer')),
                ('gender', models.CharField(default='m', max_length=1, choices=[('m', 'Mand'), ('f', 'Kvinde')])),
                ('picture', models.ImageField(blank=True, upload_to=mftutor.tutor.models.tutorpicture_upload_to)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'tutorprofiler',
                'verbose_name': 'tutorprofil',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='tutorgroupleader',
            unique_together=set([('group', 'year')]),
        ),
        migrations.AddField(
            model_name='tutor',
            name='groups',
            field=models.ManyToManyField(to='tutor.TutorGroup', blank=True, verbose_name='Arbejdsgrupper'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tutor',
            name='profile',
            field=models.ForeignKey(to='tutor.TutorProfile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tutor',
            name='rusclass',
            field=models.ForeignKey(blank=True, null=True, to='tutor.RusClass'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rus',
            name='initial_rusclass',
            field=models.ForeignKey(related_name='initial_rus_set', null=True, to='tutor.RusClass'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rus',
            name='profile',
            field=models.ForeignKey(to='tutor.TutorProfile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rus',
            name='rusclass',
            field=models.ForeignKey(null=True, to='tutor.RusClass'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='boardmember',
            name='tutor',
            field=models.ForeignKey(to='tutor.Tutor'),
            preserve_default=True,
        ),
    ]
