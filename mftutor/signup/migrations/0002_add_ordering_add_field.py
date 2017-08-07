# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0003_remove_birthday_gender'),
        ('signup', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tutorapplicationgroup',
            options={'ordering': ('priority',)},
        ),
        migrations.AddField(
            model_name='tutorapplication',
            name='assigned_groups',
            field=models.ManyToManyField(related_name='tutorapplication_assigned_set', to='tutor.TutorGroup'),
        ),
    ]
