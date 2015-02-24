from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from mftutor.tutor.auth import tutorbest_required
from mftutor.dump.views import RusDumpView, EventsDumpView

urlpatterns = patterns('',
    url(r'^rus/$', tutorbest_required(RusDumpView.as_view()), name='dump'),
    url(r'^events/$', tutorbest_required(EventsDumpView.as_view()), name='dump_events'),
)
