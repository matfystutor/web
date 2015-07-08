# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0012_auto_20150708_1343'),
    ]

    operations = [
        # Note: This overrides the old 'group' field!
        migrations.RenameField(
            model_name='tutorgroupleader',
            old_name='group_fake',
            new_name='group',
        ),
    ]
