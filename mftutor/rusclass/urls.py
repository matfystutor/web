from django.urls import path

from mftutor.rusclass.views import TutorListView, RusClassTexView
from mftutor.tutor.auth import tutorbur_required

urlpatterns = [
    path('', tutorbur_required(TutorListView.as_view()),
        name='tutor_list_pdf'),
    path('bla/', tutorbur_required(RusClassTexView.as_view()),
        name='rusclass_bla'),
]
