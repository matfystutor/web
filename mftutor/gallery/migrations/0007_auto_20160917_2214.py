from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0006_auto_20160807_1619'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='basemedia',
            options={'ordering': ['forcedOrder', 'date', 'slug'], 'select_on_save': True},
        ),
    ]
