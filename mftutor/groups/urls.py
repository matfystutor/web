from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from mftutor.tutor.auth import tutor_required
from .views import *

urlpatterns = [
    url(r'^$', login_required(GroupsView.as_view()), name='groups'),
    url(r'^(?P<group>[^/?]+)/$', tutor_required(GroupView.as_view()), name='group')                       
]
