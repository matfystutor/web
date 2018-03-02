# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_event_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='rsvp_description',
            field=models.TextField(blank=True),
        ),
    ]
