from django.conf.urls import url

from mftutor.tutor.auth import tutorbest_required, tutor_required
from .views import ShirtOptionView, ShirtPreferenceView, ShirtChoicesView

urlpatterns = [
    url(r'^options/$', tutorbest_required(ShirtOptionView.as_view()), name='shirt_options'),
    url(r'^choices/$', tutorbest_required(ShirtChoicesView.as_view()), name='shirt_choices'),
    url(r'^$', tutor_required(ShirtPreferenceView.as_view()), name='shirt_preference'),
]
