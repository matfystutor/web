from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0007_auto_20160917_2214'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='genericfile',
            options={'select_on_save': True},
        ),
        migrations.AlterModelOptions(
            name='image',
            options={'select_on_save': True},
        ),
    ]
