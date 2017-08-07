# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0015_change_primary_key'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tutorgroup',
            old_name='fake_id',
            new_name='id',
        ),
    ]
