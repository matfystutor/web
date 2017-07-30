# -*- coding: utf-8 -*-


from django.db import models, migrations


def tutorgroup_leader_data(apps, schema_editor):
    TutorGroupLeader = apps.get_model('tutor', 'TutorGroupLeader')
    for tgl in TutorGroupLeader.objects.all():
        tgl.group.leader = tgl.tutor
        tgl.group.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0025_tutorgroup_leader'),
    ]

    operations = [
        migrations.RunPython(tutorgroup_leader_data),
    ]
