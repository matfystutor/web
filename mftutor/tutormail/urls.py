from django.conf.urls import patterns, url
from ..tutor.auth import tutorbest_required
from .views import *

urlpatterns = patterns('',
    url(r'^$', tutorbest_required(EmailFormView.as_view()), name='email_form'),
    url(r'^list/$', tutorbest_required(EmailListView.as_view()), name='emails'),
    url(r'^(?P<pk>\d+)/$', tutorbest_required(EmailDetailView.as_view()), name='email'),
)
