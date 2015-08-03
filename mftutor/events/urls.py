from django.conf.urls import patterns, url
from mftutor.tutor.auth import tutorbest_required
from .views import event_detail_view, CalendarFeedView, EventListView, \
    RSVPFormView, BulkExportView, BulkImportView, EventParticipantListView, \
    EventParticipantEditView, ReminderEmailView

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
    url(r'^(?P<pk>\d+)/rsvplist/$',
        tutorbest_required(EventParticipantListView.as_view()),
        name="event_rsvps"),
    url(r'^(?P<event>\d+)/rsvplist/(?P<tutor>\d+)/$',
        tutorbest_required(EventParticipantEditView.as_view()),
        name="event_rsvp"),
    url(r'^rsvp/(\d+)/$',
        RSVPFormView.as_view(),
        name="rsvpform"),
    url(r'^export/(?P<year>\d+)/$',
        tutorbest_required(BulkExportView.as_view()),
        name="events_export"),
    url(r'^import/$',
        tutorbest_required(BulkImportView.as_view()),
        name="events_import"),
    url(r'^(?P<pk>\d+)/reminder/$',
        tutorbest_required(ReminderEmailView.as_view()),
        name="events_reminder"),
)
