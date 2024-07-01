from django.db import migrations, models


def set_visibility(apps, schema_editor):
    BaseMedia = apps.get_model('gallery', 'BaseMedia')
    # Note: We cannot access BaseMedia.DISCARDED and PUBLIC constants here
    # since 'BaseMedia' is a Django-synthesized migration model
    # and not the real models.BaseMedia class definition.
    BaseMedia.objects.filter(notPublic=True).update(visibility='discarded')
    BaseMedia.objects.filter(notPublic=False).update(visibility='public')


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0009_basemedia_visibility'),
    ]

    operations = [
        migrations.RunPython(set_visibility),
    ]
