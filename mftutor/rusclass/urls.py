from django.conf.urls import url

from mftutor.rusclass.views import TutorListView, RusClassTexView
from mftutor.tutor.auth import tutorbur_required

urlpatterns = [
    url(r'^$', tutorbur_required(TutorListView.as_view()),
        name='tutor_list_pdf'),
    url(r'^bla/$', tutorbur_required(RusClassTexView.as_view()),
        name='rusclass_bla'),
]
