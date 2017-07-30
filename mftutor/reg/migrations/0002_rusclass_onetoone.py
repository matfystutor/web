# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reg', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lightboxrusclassstate',
            name='rusclass',
            field=models.OneToOneField(to='tutor.RusClass'),
        ),
    ]
