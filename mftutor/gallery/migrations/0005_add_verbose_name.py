from django.db import migrations, models
import django.core.validators
import mftutor.gallery.utils as utils
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0004_cleanAlbums'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basemedia',
            name='caption',
            field=models.CharField(verbose_name='Overskrift', blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='basemedia',
            name='date',
            field=models.DateTimeField(null=True, verbose_name='Dato', blank=True),
        ),
        migrations.AlterField(
            model_name='basemedia',
            name='forcedOrder',
            field=models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(-10000), django.core.validators.MaxValueValidator(10000)], verbose_name='Rækkefølge', default=0),
        ),
        migrations.AlterField(
            model_name='basemedia',
            name='isCoverFile',
            field=models.BooleanField(verbose_name='Vis på forsiden', default=False),
        ),
        migrations.AlterField(
            model_name='basemedia',
            name='notPublic',
            field=models.BooleanField(verbose_name='Skjult', default=False),
        ),
        migrations.AlterField(
            model_name='basemedia',
            name='slug',
            field=models.SlugField(null=True, verbose_name='Kort titel', blank=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='description',
            field=models.TextField(blank=True, verbose_name='Beskrivelse'),
        ),
        migrations.AlterField(
            model_name='album',
            name='eventalbum',
            field=models.BooleanField(default=True, verbose_name='Arrangement'),
        ),
        migrations.AlterField(
            model_name='album',
            name='gfyear',
            field=models.PositiveSmallIntegerField(default=utils.get_gfyear, verbose_name='Årgang'),
        ),
        migrations.AlterField(
            model_name='album',
            name='publish_date',
            field=models.DateField(default=datetime.date.today, null=True, blank=True, verbose_name='Udgivelsesdato'),
        ),
        migrations.AlterField(
            model_name='album',
            name='slug',
            field=models.SlugField(verbose_name='Kort titel'),
        ),
        migrations.AlterField(
            model_name='album',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Titel'),
        ),
    ]
