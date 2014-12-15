from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
from django.contrib.auth.decorators import login_required
from ..tutor.models import Tutor, TutorGroup, BoardMember
from mftutor.tutor.auth import tutorbest_required
from ..settings import YEAR
from .models import Event
from .views import event_detail_view, CalendarFeedView, EventListView, \
    RSVPFormView, BulkExportView, BulkImportView

urlpatterns = patterns('',
    url(r'^$',
        EventListView.as_view(),
        name="events"),
    url(r'^(\d+)/$',
        event_detail_view,
        name="event"),
    url(r'^ical/$',
        CalendarFeedView.as_view(),
        name="events_ical"),
    url(r'^rsvp/(\d+)/$',
        RSVPFormView.as_view(),
        name="rsvpform"),
    url(r'^export/(?P<year>\d+)/$',
        tutorbest_required(BulkExportView.as_view()),
        name="events_export"),
    url(r'^import/$',
        tutorbest_required(BulkImportView.as_view()),
        name="events_import"),
)
