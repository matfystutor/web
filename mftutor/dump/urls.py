from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from mftutor.tutor.auth import tutorbest_required
from mftutor.dump.views import RusDumpView

urlpatterns = patterns('',
    url(r'^rus/$', tutorbest_required(RusDumpView.as_view()), name='dump'),
)
