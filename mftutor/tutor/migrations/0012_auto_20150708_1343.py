# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def set_tgl_group(apps, schema_editor):
    TutorGroupLeader = apps.get_model('tutor', 'TutorGroupLeader')
    for tgl in TutorGroupLeader.objects.all():
        tgl.group_fake = tgl.group
        tgl.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0011_tutorgroupleader_group_fake'),
    ]

    operations = [
        migrations.RunPython(set_tgl_group),
    ]
