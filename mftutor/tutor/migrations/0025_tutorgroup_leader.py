# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0024_remove_tutorgroupleader_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorgroup',
            name='leader',
            field=models.ForeignKey(verbose_name='Gruppeansvarlig', to='tutor.Tutor', null=True),
        ),
    ]
