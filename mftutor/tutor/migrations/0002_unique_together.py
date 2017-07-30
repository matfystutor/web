# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tutor',
            unique_together=set([('profile', 'year')]),
        ),
    ]
