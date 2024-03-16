from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0002_auto_20160502_1538'),
    ]

    operations = [
        migrations.AddField(
            model_name='basemedia',
            name='isCoverFile',
            field=models.BooleanField(default=False),
        ),
    ]
