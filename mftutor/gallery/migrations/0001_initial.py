from django.db import migrations, models
import datetime
import mftutor.gallery.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('publish_date', models.DateField(default=datetime.date.today, blank=True, null=True)),
                ('eventalbum', models.BooleanField(default=True)),
                ('gfyear', models.PositiveSmallIntegerField(default=mftutor.gallery.models.get_gfyear)),
                ('slug', models.SlugField()),
                ('description', models.TextField(blank=True)),
                ('oldFolder', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'ordering': ['gfyear', '-eventalbum', 'oldFolder', 'publish_date'],
            },
        ),
        migrations.CreateModel(
            name='BaseMedia',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('notPublic', models.BooleanField(default=False)),
                ('caption', models.CharField(blank=True, max_length=200)),
                ('slug', models.SlugField(blank=True)),
            ],
            options={
                'ordering': ['date', 'slug'],
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('basemedia_ptr', models.OneToOneField(auto_created=True, to='gallery.BaseMedia', primary_key=True, serialize=False, parent_link=True, on_delete=models.CASCADE)),
                ('image', models.ImageField(blank=True, null=True, upload_to=mftutor.gallery.models.file_name)),
            ],
            bases=('gallery.basemedia',),
        ),
        migrations.AddField(
            model_name='basemedia',
            name='album',
            field=models.ForeignKey(to='gallery.Album', related_name='basemedia', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='album',
            unique_together=set([('gfyear', 'slug')]),
        ),
        migrations.AlterUniqueTogether(
            name='basemedia',
            unique_together=set([('album', 'slug')]),
        ),
    ]
