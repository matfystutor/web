# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsPost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('title', models.CharField(verbose_name='Titel', max_length=200)),
                ('posted', models.DateTimeField(verbose_name='Dato')),
                ('body', models.TextField(verbose_name='Indhold')),
                ('group_handle', models.CharField(max_length=20)),
                ('author', models.ForeignKey(verbose_name='Forfatter', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'nyhed',
                'verbose_name_plural': 'nyheder',
            },
            bases=(models.Model,),
        ),
    ]
