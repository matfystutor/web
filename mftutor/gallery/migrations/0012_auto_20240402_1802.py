# Generated by Django 2.2.13 on 2024-04-02 16:02

from django.db import migrations, models
import mftutor.gallery.utils


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0011_remove_basemedia_notpublic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='file',
            field=models.ImageField(upload_to=mftutor.gallery.utils.file_name),
        ),
    ]