# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0003_remove_birthday_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorgroup',
            name='year',
            field=models.IntegerField(null=True, verbose_name='Tutor\xe5r'),
        ),
    ]
