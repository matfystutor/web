from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView, DeleteView
from ..tutor.auth import tutorbest_required
from .views import (
    GuidesView, MinutesView, PublicationsView, UploadDocumentView,
    EditDocumentView, DeleteDocumentView)
from .models import Document
from .feed import MinutesFeed

urlpatterns = patterns('',
    url(r'^guides/(?:(?P<year>\d+)/)?$',
        GuidesView.as_view(), name='list_guides'),
    url(r'^referater/(?:(?P<year>\d+)/)?$',
        MinutesView.as_view(), name='list_referater'),
    url(r'^referater/feed/$', MinutesFeed(), name='referater_feed'),
    url(r'^udgivelser/(?:(?P<year>\d+)/)?$',
        PublicationsView.as_view(), name='list_udgivelser'),
    url(r'^upload/$', UploadDocumentView.as_view(), name='upload_document'),
    url(r'^edit/(?P<pk>\d+)/$',
        EditDocumentView.as_view(), name='edit_document'),
    url(r'^delete/(?P<pk>\d+)/$',
        DeleteDocumentView.as_view(),
        name='document_delete'),
)
