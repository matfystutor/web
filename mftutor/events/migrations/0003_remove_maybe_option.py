# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_change_old_maybes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventparticipant',
            name='status',
            field=models.CharField(max_length=10, verbose_name=b'Tilbagemelding', choices=[(b'yes', b'Kommer'), (b'no', b'Kommer ikke')]),
        ),
    ]
