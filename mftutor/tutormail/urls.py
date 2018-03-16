from django.conf.urls import patterns, url
from ..tutor.auth import groupleader_required
from mftutor.tutormail.views import EmailFormView

urlpatterns = patterns('',
    url(r'^$', groupleader_required(EmailFormView.as_view()), name='email_form',
        kwargs={'recipients': 'tutor'}),
    url(r'^(?P<recipients>hold|rus|rusarrived)/$',
        groupleader_required(EmailFormView.as_view()),
        name='email_form_recipients'),
    # url(r'^list/$', tutorbest_required(EmailListView.as_view()), name='emails'),
    # url(r'^(?P<pk>\d+)/$', tutorbest_required(EmailDetailView.as_view()), name='email'),
)
