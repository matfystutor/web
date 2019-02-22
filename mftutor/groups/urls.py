from django.contrib.auth.decorators import login_required
from django.urls import path

from mftutor.tutor.auth import tutor_required
from .views import *

urlpatterns = [
    path('', login_required(GroupsView.as_view()), name='groups'),
    path('<group>/', tutor_required(GroupView.as_view()), name='group')
]
