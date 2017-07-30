# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0019_add_year'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tutor',
            old_name='groups2',
            new_name='groups',
        ),
    ]
