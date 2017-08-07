# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0020_remove_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutor',
            name='groups',
            field=models.ManyToManyField(to='tutor.TutorGroup', verbose_name='Arbejdsgrupper', blank=True),
        ),
    ]
