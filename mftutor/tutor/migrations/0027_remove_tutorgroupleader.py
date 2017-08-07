# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0026_tutorgroup_leader_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tutorgroupleader',
            name='group',
        ),
        migrations.RemoveField(
            model_name='tutorgroupleader',
            name='tutor',
        ),
        migrations.DeleteModel(
            name='TutorGroupLeader',
        ),
    ]
