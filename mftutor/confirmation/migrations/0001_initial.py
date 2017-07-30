# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Confirmation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('study', models.CharField(verbose_name='Studium samt sidefag/tilvalg', max_length=500, blank=True)),
                ('experience', models.CharField(verbose_name='Tidligere erfaring som holdtutor', max_length=60, blank=True)),
                ('resits', models.CharField(verbose_name='Reeksamener i rusugen', max_length=500, blank=True)),
                ('priorities', models.CharField(verbose_name='Ønskede studieretninger', max_length=60, blank=True)),
                ('firstaid', models.CharField(verbose_name='Førstehjælpskursus', max_length=60, blank=True)),
                ('rusfriends', models.CharField(verbose_name='Bekendte nye studerende', max_length=500, blank=True)),
                ('comment', models.CharField(verbose_name='Kommentar', max_length=500, blank=True)),
                ('internal_notes', models.CharField(verbose_name='Notat', max_length=500, blank=True)),
                ('tutor', models.OneToOneField(to='tutor.Tutor')),
            ],
            options={
                'ordering': ('tutor',),
            },
            bases=(models.Model,),
        ),
    ]
