from django.conf.urls import url
from django.urls import path, re_path
import mftutor.gallery.views as views

urlpatterns = [
    # Gallery overview
    url(r'^$',
        views.gallery,
        name='gallery_index'),
    url(r'^(?P<gfyear>\d+)$',
        views.gallery,
        name='gfyear'),

    # Album overview
    url(r'^(?P<gfyear>\d+)/(?P<album_slug>[^/]+)$',
        views.album,
        name='album'),

    # Single images
    url(r'^(?P<gfyear>\d+)/(?P<album_slug>[^/]+)/(?P<image_slug>[^/]+)$',
        views.image,
        name='image'),

    # Bulk-update BaseMedia.visibility
    url(r'^set_visibility/$',
        views.set_visibility,
        name='set_image_visibility'),

    # JFU upload
    url(r'^upload/',
        views.upload,
        name='jfu_upload'),

    # RSS feed
    url(r'^album\.rss$',
        views.AlbumFeed(),
        name='album_rss'),
]
