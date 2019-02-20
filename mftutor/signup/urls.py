from django.conf.urls import url

from mftutor.signup.views import (
    SignupImportView, SignupListView, TutorGroupView,
    GroupLeaderView, TutorCreateView)
from mftutor.tutor.auth import tutorbest_required

urlpatterns = [
    url(r'^import/$', tutorbest_required(SignupImportView.as_view()), name='signup_import'),
    url(r'^$', tutorbest_required(SignupListView.as_view()), name='signup_list'),
    url(r'^groups/$', tutorbest_required(TutorGroupView.as_view()), name='signup_groups'),
    url(r'^groupleader/$', tutorbest_required(GroupLeaderView.as_view()), name='signup_groupleader'),
    url(r'^create/$', tutorbest_required(TutorCreateView.as_view()), name='signup_create'),
]
