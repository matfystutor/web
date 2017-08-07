# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='year',
            field=models.IntegerField(verbose_name='Tutor\xe5r'),
        ),
    ]
