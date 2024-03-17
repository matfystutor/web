from PIL import Image as PILImage
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.urls import reverse
from django.test import TestCase, override_settings
from mftutor.gallery import views
from mftutor.gallery.models import Album, Image
import tempfile


class SimpleAlbumTest(TestCase):
    def test_empty_album(self):
        self.assertFalse(Album.objects.exists())
        instance = Album.objects.create(title="Album Title", slug="album-title")
        instance.full_clean()
        self.assertTrue(Album.objects.exists())


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class SimpleMediaTest(TestCase):
    def setUp(self):
        album = Album.objects.create(title="Album Title", slug="album-title")
        album.full_clean()

    def generate_image(self, suffix):
        album = Album.objects.all()[0]

        temp_file = tempfile.NamedTemporaryFile(suffix=suffix)
        PILImage.new("RGB", (100, 100)).save(temp_file)

        Image(file=temp_file.name, album=album).save()

        try:
            Image.objects.all()[0].file.crop["200x200"]
        except ValidationError:
            self.fail(
                "VersatileImageField Raised ValidationError on a good %s image" % suffix
            )
        self.assertEqual(len(Image.objects.all()), 1)
        self.assertIsInstance(album.basemedia.select_subclasses()[0], Image)

    def test_simple_jpg_album(self):
        self.generate_image(".jpg")

    def test_simple_png_album(self):
        self.generate_image(".png")

    def test_simple_gif_album(self):
        self.generate_image(".gif")


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class CorruptedMediaTest(TestCase):
    def setUp(self):
        album = Album.objects.create(
            title="Corrupt Album Title", slug="corrupt-album-title"
        )
        album.full_clean()

    def test_truncated_jpg_album(self):
        album = Album.objects.all()[0]

        temp_file = tempfile.NamedTemporaryFile(suffix=".jpg")
        PILImage.new("RGB", (100, 100)).save(temp_file, "jpeg")
        temp_file.truncate(800)

        instance = Image(file=temp_file.name, album=album)
        instance.full_clean()
        with self.assertLogs(level="ERROR"):
            with self.assertRaises(ValidationError):
                instance.save()

        self.assertEqual(len(Image.objects.all()), 0)


class GalleryViewTest(TestCase):
    def setUp(self):
        super().setUp()
        self.album = Album.objects.create(gfyear=2018, title="Test", slug="test")
        # Create two images
        self.create_image("image1")
        self.create_image("image2")

    def create_image(self, slug):
        with tempfile.NamedTemporaryFile(suffix=".png") as im:
            PILImage.new("RGB", (100, 100)).save(im)
            im.seek(0)
            contents = ContentFile(im.read(), "im.png")
            image = Image(
                file=contents, album=self.album, slug=slug, visibility=Image.PUBLIC
            )
            image.full_clean()
            image.save()
            return image

    def test_album_count(self):
        response = self.client.get(reverse("gallery_index"))
        self.assertEquals(1, len(list(response.context["albumSets"])))
