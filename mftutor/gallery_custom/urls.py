from django.conf.urls import *

from mftutor.tutor.auth import tutor_required

from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy
from photologue.views import (PhotoListView, PhotoDetailView, GalleryListView,
GalleryDetailView, PhotoArchiveIndexView, PhotoDateDetailView, PhotoDayArchiveView,
PhotoYearArchiveView, PhotoMonthArchiveView, GalleryArchiveIndexView, GalleryYearArchiveView,
GalleryDateDetailView, GalleryDayArchiveView, GalleryMonthArchiveView, GalleryDateDetailOldView,
GalleryDayArchiveOldView, GalleryMonthArchiveOldView, PhotoDateDetailOldView,
PhotoDayArchiveOldView, PhotoMonthArchiveOldView)

urlpatterns = [
    # Standard view
    url(r'^$',
        tutor_required(GalleryArchiveIndexView.as_view()),
        name='gallery'),

    url(r'^gallery/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$',
        tutor_required(GalleryDateDetailView.as_view(month_format='%m')),
        name='gallery-detail'),
    url(r'^gallery/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/$',
        tutor_required(GalleryDayArchiveView.as_view(month_format='%m')),
        name='gallery-archive-day'),
    url(r'^gallery/(?P<year>\d{4})/(?P<month>[0-9]{2})/$',
        tutor_required(GalleryMonthArchiveView.as_view(month_format='%m')),
        name='gallery-archive-month'),
    url(r'^gallery/(?P<year>\d{4})/$',
        tutor_required(GalleryYearArchiveView.as_view()),
        name='pl-gallery-archive-year'),
    url(r'^gallery/$',
        tutor_required(GalleryArchiveIndexView.as_view()),
        name='pl-gallery-archive'),
    url(r'^$',
        tutor_required(RedirectView.as_view(
            url=reverse_lazy('photologue:pl-gallery-archive'), permanent=True)),
        name='pl-photologue-root'),
    url(r'^gallery/(?P<slug>[\-\d\w]+)/$',
        tutor_required(GalleryDetailView.as_view()), name='pl-gallery'),
    url(r'^gallerylist/$',
        tutor_required(GalleryListView.as_view()),
        name='gallery-list'),

    url(r'^photo/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$',
        tutor_required(PhotoDateDetailView.as_view(month_format='%m')),
        name='photo-detail'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/$',
        tutor_required(PhotoDayArchiveView.as_view(month_format='%m')),
        name='photo-archive-day'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[0-9]{2})/$',
        tutor_required(PhotoMonthArchiveView.as_view(month_format='%m')),
        name='photo-archive-month'),
    url(r'^photo/(?P<year>\d{4})/$',
        tutor_required(PhotoYearArchiveView.as_view()),
        name='pl-photo-archive-year'),
    url(r'^photo/$',
        tutor_required(PhotoArchiveIndexView.as_view()),
        name='pl-photo-archive'),

    url(r'^photo/(?P<slug>[\-\d\w]+)/$',
        tutor_required(PhotoDetailView.as_view()),
        name='pl-photo'),
    url(r'^photolist/$',
        tutor_required(PhotoListView.as_view()),
        name='photo-list'),

    # Deprecated URLs.
    url(r'^gallery/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$',
        tutor_required(GalleryDateDetailOldView.as_view()),
        name='pl-gallery-detail'),
    url(r'^gallery/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$',
        tutor_required(GalleryDayArchiveOldView.as_view()),
        name='pl-gallery-archive-day'),
    url(r'^gallery/(?P<year>\d{4})/(?P<month>[a-z]{3})/$',
        tutor_required(GalleryMonthArchiveOldView.as_view()),
        name='pl-gallery-archive-month'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$',
        tutor_required(PhotoDateDetailOldView.as_view()),
        name='pl-photo-detail'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$',
        tutor_required(PhotoDayArchiveOldView.as_view()),
        name='pl-photo-archive-day'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[a-z]{3})/$',
        tutor_required(PhotoMonthArchiveOldView.as_view()),
name='pl-photo-archive-month')
]
