from django.urls import path, re_path

from .feed import MinutesFeed
from .views import (
    GuidesView, MinutesView, PublicationsView, UploadDocumentView,
    EditDocumentView, DeleteDocumentView)

urlpatterns = [
    re_path('guides/(?:(?P<year>\d+)/)?$',
            GuidesView.as_view(), name='list_guides'),
    re_path(r'^referater/(?:(?P<year>\d+)/)?$',
            MinutesView.as_view(), name='list_referater'),
    path('referater/feed/', MinutesFeed(), name='referater_feed'),
    re_path(r'^udgivelser/(?:(?P<year>\d+)/)?$',
            PublicationsView.as_view(), name='list_udgivelser'),
    path('upload/', UploadDocumentView.as_view(), name='upload_document'),
    path('edit/<int:pk>/',
         EditDocumentView.as_view(), name='edit_document'),
    path('delete/<int:pk>/',
         DeleteDocumentView.as_view(),
         name='document_delete'),
]
