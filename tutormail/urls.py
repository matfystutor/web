from django.conf.urls import patterns, url
from .views import *
from tutor.auth import tutorbest_required

urlpatterns = patterns('',
    url(r'^$', tutorbest_required(EmailListView.as_view()), name='emails'),
    url(r'^(?P<pk>\d+)/$', tutorbest_required(EmailDetailView.as_view()), name='email'),
)
