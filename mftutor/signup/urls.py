from django.urls import path

from mftutor.signup.views import (
    SignupImportView, SignupListView, TutorGroupView,
    GroupLeaderView, TutorCreateView)
from mftutor.tutor.auth import tutorbest_required

urlpatterns = [
    path('import/', tutorbest_required(SignupImportView.as_view()), name='signup_import'),
    path('', tutorbest_required(SignupListView.as_view()), name='signup_list'),
    path('groups/', tutorbest_required(TutorGroupView.as_view()), name='signup_groups'),
    path('groupleader/', tutorbest_required(GroupLeaderView.as_view()), name='signup_groupleader'),
    path('create/', tutorbest_required(TutorCreateView.as_view()), name='signup_create'),
]
