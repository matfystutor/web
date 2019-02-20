from django.conf.urls import url

from mftutor.dump.views import TutorDumpView, RusDumpView, EventsDumpView, GroupsDumpView
from mftutor.tutor.auth import tutorbest_required

urlpatterns = [
    url(r'^tutor/$', tutorbest_required(TutorDumpView.as_view()), name='dump_tutor'),
    url(r'^rus/$', tutorbest_required(RusDumpView.as_view()), name='dump_rus'),
    url(r'^events/$', tutorbest_required(EventsDumpView.as_view()), name='dump_events'),
    url(r'^groups/$', tutorbest_required(GroupsDumpView.as_view()), name='dump_groups'),
]
