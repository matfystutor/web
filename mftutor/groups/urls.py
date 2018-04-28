from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from .views import *
from mftutor.tutor.auth import tutor_required

urlpatterns = patterns('',
    url(r'^$', login_required(GroupsView.as_view()), name='groups'),
    url(r'^(?P<group>[^/?]+)/$', tutor_required(GroupView.as_view()), name='group')                       
)
