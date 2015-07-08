from __future__ import unicode_literals

from django.conf.urls import patterns, url

from mftutor.signup.views import SignupImportView, SignupListView

urlpatterns = patterns(
    '',
    url(r'^import/$', SignupImportView.as_view(), name='signup_import'),
    url(r'^$', SignupListView.as_view(), name='signup_list'),
)
