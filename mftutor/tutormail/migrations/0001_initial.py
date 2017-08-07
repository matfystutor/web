# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('sender', models.CharField(blank=True, max_length=100, verbose_name='Fra')),
                ('recipient', models.CharField(blank=True, max_length=100, verbose_name='Til')),
                ('subject', models.CharField(blank=True, max_length=100, verbose_name='Emne')),
                ('body', models.TextField(blank=True, verbose_name='Tekst')),
                ('kind', models.CharField(blank=True, max_length=100, verbose_name='Slags')),
                ('sent', models.DateTimeField(null=True, blank=True, verbose_name='Sendt')),
                ('retain', models.BooleanField(verbose_name='Tilbagehold', default=False)),
                ('manually_changed', models.DateTimeField(null=True, blank=True, verbose_name='Ændret manuelt')),
                ('archive', models.BooleanField(verbose_name='Arkiveret', default=False)),
                ('html', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['kind', 'recipient', 'pk'],
            },
            bases=(models.Model,),
        ),
    ]
