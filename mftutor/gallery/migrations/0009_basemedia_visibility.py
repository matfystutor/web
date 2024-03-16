from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0008_auto_20160917_2233'),
    ]

    operations = [
        migrations.AddField(
            model_name='basemedia',
            name='visibility',
            field=models.CharField(verbose_name='Synlighed', max_length=10, default='new', choices=[('public', 'Synligt'), ('discarded', 'Frasorteret'), ('sensitive', 'Skjult'), ('delete', 'Slet'), ('new', 'Ubesluttet')]),
        ),
    ]
