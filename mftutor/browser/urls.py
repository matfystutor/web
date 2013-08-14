from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import ProfileView, RusClassView, GroupView, SearchView

urlpatterns = patterns('',
    url(r'^search/$', login_required(SearchView.as_view()),
        name='browser_search'),
    url(r'^profile/(?P<studentnumber>[0-9a-zA-Z]+)/$', login_required(ProfileView.as_view()),
        name='browser_profile'),
    url(r'^rusclass/(?P<year>\d+)/(?P<handle>[a-z0-9]+)/$', login_required(RusClassView.as_view()),
        name='browser_rusclass'),
    url(r'^group/(?P<year>\d+)/(?P<handle>[a-z0-9]+)/$', login_required(GroupView.as_view()),
        name='browser_group'),
    )
