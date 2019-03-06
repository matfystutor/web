from django.urls import path

from mftutor.dump.views import TutorDumpView, RusDumpView, EventsDumpView, GroupsDumpView
from mftutor.tutor.auth import tutorbest_required

urlpatterns = [
    path('tutor/', tutorbest_required(TutorDumpView.as_view()), name='dump_tutor'),
    path('rus/', tutorbest_required(RusDumpView.as_view()), name='dump_rus'),
    path('events/', tutorbest_required(EventsDumpView.as_view()), name='dump_events'),
    path('groups/', tutorbest_required(GroupsDumpView.as_view()), name='dump_groups'),
]
