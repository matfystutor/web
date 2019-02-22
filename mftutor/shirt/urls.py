from django.urls import path

from mftutor.tutor.auth import tutorbest_required, tutor_required
from .views import ShirtOptionView, ShirtPreferenceView, ShirtChoicesView

urlpatterns = [
    path('', tutor_required(ShirtPreferenceView.as_view()), name='shirt_preference'),
    path('options/', tutorbest_required(ShirtOptionView.as_view()), name='shirt_options'),
    path('choices/', tutorbest_required(ShirtChoicesView.as_view()), name='shirt_choices'),
]
