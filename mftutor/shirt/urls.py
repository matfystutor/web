from django.conf.urls import patterns, url
from mftutor.tutor.auth import tutorbest_required, tutor_required
from .views import ShirtOptionView, ShirtPreferenceView

urlpatterns = patterns('',
    url(r'^options/$', tutorbest_required(ShirtOptionView.as_view()), name='shirt_options'),
    url(r'^$', tutor_required(ShirtPreferenceView.as_view()), name='shirt_preference'),
)
