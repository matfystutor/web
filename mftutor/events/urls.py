from django.urls import path

from mftutor.tutor.auth import tutorbest_required
from .views import event_detail_view, CalendarFeedView, EventListView, \
    RSVPFormView, BulkExportView, BulkImportView, EventParticipantListView, \
    EventParticipantEditView, ReminderEmailView

urlpatterns = [
    path('',
         EventListView.as_view(),
         name="events"),
    path('year/<int:year>/',
         EventListView.as_view(),
         name="events_year"),
    path('<int:eventid>/',
         event_detail_view,
         name="event"),
    path('ical/',
         CalendarFeedView.as_view(),
         name="events_ical"),
    path('<int:pk>/rsvplist/',
         tutorbest_required(EventParticipantListView.as_view()),
         name="event_rsvps"),
    path('<int:event>/rsvplist/<int:tutor>/',
         tutorbest_required(EventParticipantEditView.as_view()),
         name="event_rsvp"),
    path('rsvp/<int:pk>/',
         RSVPFormView.as_view(),
         name="rsvpform"),
    path('export/<int:year>/',
         tutorbest_required(BulkExportView.as_view()),
         name="events_export"),
    path('import/',
         tutorbest_required(BulkImportView.as_view()),
         name="events_import"),
    path('<int:pk>/reminder/',
         tutorbest_required(ReminderEmailView.as_view()),
         name="events_reminder"),
]
