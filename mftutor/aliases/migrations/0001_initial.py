# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alias',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('source', models.CharField(max_length=50)),
                ('destination', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['source', 'destination'],
                'verbose_name_plural': 'aliaser',
                'verbose_name': 'alias',
            },
        ),
        migrations.AlterUniqueTogether(
            name='alias',
            unique_together=set([('source', 'destination')]),
        ),
    ]
