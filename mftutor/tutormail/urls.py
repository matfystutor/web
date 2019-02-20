from django.conf.urls import url

from mftutor.tutormail.views import EmailFormView
from ..tutor.auth import groupleader_required

urlpatterns = [
    url(r'^$', groupleader_required(EmailFormView.as_view()), name='email_form',
        kwargs={'recipients': 'tutor'}),
    url(r'^(?P<recipients>hold|rus|rusarrived)/$',
        groupleader_required(EmailFormView.as_view()),
        name='email_form_recipients'),
    # url(r'^list/$', tutorbest_required(EmailListView.as_view()), name='emails'),
    # url(r'^(?P<pk>\d+)/$', tutorbest_required(EmailDetailView.as_view()), name='email'),
]
