# -*- coding: utf-8 -*-


from django.db import models, migrations


def assign_fake_group_ids(apps, schema_editor):
    TutorGroup = apps.get_model('tutor', 'TutorGroup')
    for i, tg in enumerate(TutorGroup.objects.all()):
        tg.fake_id = i + 1
        tg.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0005_tutorgroup_fake_id'),
    ]

    operations = [
        migrations.RunPython(assign_fake_group_ids),
    ]
