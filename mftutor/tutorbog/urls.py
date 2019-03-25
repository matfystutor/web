from django.urls import path

from mftutor.tutorbog.views import secret_view

urlpatterns = [
    path('<secret>/', secret_view),
]
