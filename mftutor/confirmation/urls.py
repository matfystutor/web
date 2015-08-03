from django.conf.urls import patterns, url
from mftutor.tutor.auth import tutorbest_required
from .views import OwnConfirmationView, ConfirmationTableView, EditNoteView, ConfirmationCardView

urlpatterns = patterns('',
    url(r'^$', OwnConfirmationView.as_view(), name='own_confirmation'),
    url(r'^table/$', tutorbest_required(ConfirmationTableView.as_view()), name='confirmation_table'),
    url(r'^card/$', tutorbest_required(ConfirmationCardView.as_view()), name='confirmation_card'),
    url(r'^editnote/$', EditNoteView.as_view(), name='confirmation_edit_note'),
)
