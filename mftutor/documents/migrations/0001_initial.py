# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mftutor.documents.models

from ... import settings


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('title', models.CharField(max_length=100, verbose_name='Titel')),
                ('year', models.IntegerField(verbose_name='Tutorår', default=settings.YEAR)),
                ('published', models.DateField(verbose_name='Dato')),
                ('time_of_upload', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(max_length=30, choices=[('guides', 'Guide'), ('referater', 'Referat'), ('udgivelser', 'Udgivelse')], verbose_name='Type')),
                ('doc_file', models.FileField(verbose_name='Dokument', upload_to=mftutor.documents.models.Document_upload_to)),
            ],
            options={
                'ordering': ('-year', 'title'),
            },
            bases=(models.Model,),
        ),
    ]
