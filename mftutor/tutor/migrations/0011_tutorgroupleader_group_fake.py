# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0010_auto_20150708_1340'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorgroupleader',
            name='group_fake',
            field=models.ForeignKey(related_name='+', to_field='fake_id', to='tutor.TutorGroup', null=True),
        ),
    ]
