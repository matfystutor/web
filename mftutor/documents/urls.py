from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView, DeleteView
from ..tutor.auth import tutorbest_required
from .views import DocumentListView, UploadDocumentView, EditDocumentView, DeleteDocumentView
from .models import Document

urlpatterns = patterns('',
    url(r'^(?P<kind>guides|referater|udgivelser)/(?:(?P<year>\d+)/)?$', DocumentListView.as_view(), name='list_documents'),
    url(r'^upload/$', UploadDocumentView.as_view(), name='upload_document'),
    url(r'^edit/(?P<pk>\d+)/$', EditDocumentView.as_view(), name='edit_document'),
    url(r'^delete/(?P<pk>\d+)/$',
        DeleteDocumentView.as_view(),
        name='document_delete'),
)
