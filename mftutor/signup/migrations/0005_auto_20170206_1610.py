# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('signup', '0004_auto_20150805_1658'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tutorapplication',
            name='buret',
        ),
        migrations.AddField(
            model_name='tutorapplication',
            name='tutortype',
            field=models.CharField(default='hold', max_length=20),
            preserve_default=False,
        ),
    ]
