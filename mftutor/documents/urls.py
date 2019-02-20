from django.conf.urls import url

from .feed import MinutesFeed
from .views import (
    GuidesView, MinutesView, PublicationsView, UploadDocumentView,
    EditDocumentView, DeleteDocumentView)

urlpatterns = [
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
]
