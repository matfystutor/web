from django.db import migrations, models
import django.core.validators
import mftutor.gallery.models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenericFile',
            fields=[
                ('basemedia_ptr', models.OneToOneField(parent_link=True, primary_key=True, auto_created=True, to='gallery.BaseMedia', serialize=False, on_delete=models.CASCADE)),
                ('originalFile', models.FileField(upload_to=mftutor.gallery.models.file_name, blank=True)),
                ('file', models.FileField(upload_to=mftutor.gallery.models.file_name)),
            ],
            bases=('gallery.basemedia',),
        ),
        migrations.AlterModelOptions(
            name='basemedia',
            options={'ordering': ['forcedOrder', 'date', 'slug']},
        ),
        migrations.RenameField(
            model_name='image',
            old_name='image',
            new_name='file',
        ),
        migrations.AddField(
            model_name='basemedia',
            name='forcedOrder',
            field=models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(-10000), django.core.validators.MaxValueValidator(10000)], default=0),
        ),
        migrations.AddField(
            model_name='basemedia',
            name='type',
            field=models.CharField(choices=[('I', 'Image'), ('V', 'Video'), ('A', 'Audio'), ('O', 'Other')], max_length=1, default='O'),
        ),
        migrations.AlterField(
            model_name='basemedia',
            name='slug',
            field=models.SlugField(null=True, blank=True),
        ),
    ]
