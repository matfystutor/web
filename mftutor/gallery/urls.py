from django.conf.urls import url
from django.urls import path, re_path
import mftutor.gallery.views as views

urlpatterns = [
    # Gallery overview
    re_path(r'^$',
        views.gallery,
        name='gallery_index'),
    re_path(r'^(?P<gfyear>\d+)$',
        views.gallery,
        name='gfyear'),

    # Album overview
    re_path(r'^(?P<gfyear>\d+)/(?P<album_slug>[^/]+)$',
        views.album,
        name='album'),

    # Single images
    re_path(r'^(?P<gfyear>\d+)/(?P<album_slug>[^/]+)/(?P<image_slug>[^/]+)$',
        views.image,
        name='image'),

    # Bulk-update BaseMedia.visibility
    re_path(r'^set_visibility/$',
        views.set_visibility,
        name='set_image_visibility'),

    # JFU upload
    re_path(r'^upload/',
        views.upload,
        name='jfu_upload'),

    # RSS feed
    re_path(r'^album\.rss$',
        views.AlbumFeed(),
        name='album_rss'),
]
