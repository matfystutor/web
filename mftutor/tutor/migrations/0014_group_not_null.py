# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0013_substitute_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorgroupleader',
            name='group',
            field=models.ForeignKey(related_name='+', to='tutor.TutorGroup', to_field='fake_id'),
        ),
    ]
