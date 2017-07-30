# -*- coding: utf-8 -*-


from django.db import models, migrations


def populate_tutor_in_group(apps, schema_editor):
    Tutor = apps.get_model('tutor', 'Tutor')
    TutorInTutorGroup = apps.get_model('tutor', 'TutorInTutorGroup')
    for tu in Tutor.objects.all():
        for tg in tu.groups.all():
            TutorInTutorGroup(tutor=tu, tutorgroup=tg).save()


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0008_tutorintutorgroup'),
    ]

    operations = [
        migrations.RunPython(populate_tutor_in_group),
    ]
