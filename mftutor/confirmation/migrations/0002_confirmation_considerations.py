# Generated by Django 2.2.2 on 2020-07-03 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('confirmation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='confirmation',
            name='considerations',
            field=models.CharField(blank=True, max_length=500, verbose_name='Hensyn'),
        ),
    ]