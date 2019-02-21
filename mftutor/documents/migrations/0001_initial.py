# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mftutor.documents.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Titel')),
                ('year', models.IntegerField(verbose_name='Tutorår')),
                ('published', models.DateField(verbose_name='Dato')),
                ('time_of_upload', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(max_length=30, choices=[('guides', 'Guide'), ('referater', 'Referat'), ('udgivelser', 'Udgivelse')], verbose_name='Type')),
                ('doc_file', models.FileField(upload_to=mftutor.documents.models.Document_upload_to, verbose_name='Dokument')),
            ],
            options={
                'ordering': ('-year', 'title'),
            },
        ),
    ]
