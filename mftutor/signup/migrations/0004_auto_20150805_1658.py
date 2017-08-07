# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('signup', '0003_assignedgroupleader'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(verbose_name='Tutor\xe5r')),
                ('text', models.TextField()),
                ('subject', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='tutorapplication',
            name='email_template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='signup.EmailTemplate', null=True),
        ),
    ]
