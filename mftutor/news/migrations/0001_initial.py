# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Titel')),
                ('posted', models.DateTimeField(verbose_name='Dato')),
                ('body', models.TextField(verbose_name='Indhold')),
                ('group_handle', models.CharField(max_length=20)),
                ('year', models.IntegerField(default=0)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Forfatter')),
            ],
            options={
                'verbose_name_plural': 'nyheder',
                'verbose_name': 'nyhed',
            },
        ),
    ]
