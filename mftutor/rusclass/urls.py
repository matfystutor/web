from django.conf.urls import patterns, url

from mftutor.rusclass.views import TutorListView

urlpatterns = patterns('',
    url(r'^$', TutorListView.as_view(), name='tutor_list_pdf'),
)
