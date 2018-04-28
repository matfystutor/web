# -*- coding: utf-8 -*-


from django.db import models, migrations


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
                'verbose_name': 'alias',
                'verbose_name_plural': 'aliaser',
                'ordering': ['source', 'destination'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='alias',
            unique_together=set([('source', 'destination')]),
        ),
    ]
