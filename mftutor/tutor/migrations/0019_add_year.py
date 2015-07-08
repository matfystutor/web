# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_year(apps, schema_editor):
    Tutor = apps.get_model('tutor', 'Tutor')
    TutorGroup = apps.get_model('tutor', 'TutorGroup')
    TutorGroupLeader = apps.get_model('tutor', 'TutorGroupLeader')

    groupyears = {}
    for tg in TutorGroup.objects.all():
        if tg.year != None:
            groupyears[tg.year, tg.handle] = tg

    for tu in Tutor.objects.all():
        for tg in list(tu.groups.all()):
            try:
                tg_with_year = groupyears[tu.year, tg.handle]
            except KeyError:
                tg_with_year = TutorGroup(
                    year=tu.year, handle=tg.handle,
                    name=tg.name, visible=tg.visible)
                tg_with_year.save()
                groupyears[tu.year, tg.handle] = tg_with_year
            tu.groups2.add(tg_with_year)

    for tgl in TutorGroupLeader.objects.all():
        if tgl.group.year == None:
            tgl.group = groupyears[tgl.year, tgl.group.handle]
            tgl.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0018_tutor_groups2'),
    ]

    operations = [
        migrations.RunPython(add_year),
    ]
