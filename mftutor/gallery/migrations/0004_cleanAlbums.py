from django.db import migrations, models


def cleanAlbums(apps, schema_editor):
    Album = apps.get_model("gallery", "Album")
    for a in Album.objects.all():
        a.clean()
        a.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0003_basemedia_iscoverfile'),
    ]

    operations = [
        migrations.RunPython(cleanAlbums)
    ]
