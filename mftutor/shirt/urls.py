from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from ..tutor.auth import tutorbest_required
from .views import ShirtOptionView, ShirtPreferenceView

urlpatterns = patterns('',
    url(r'^options/$', tutorbest_required(ShirtOptionView.as_view()), name='shirt_options'),
    url(r'^$', login_required(ShirtPreferenceView.as_view()), name='shirt_preference'),
)
