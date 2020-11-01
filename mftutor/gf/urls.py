from django.urls import path
from mftutor.tutor.auth import tutorbest_required, tutor_required
from mftutor.gf import views

urlpatterns = [
    path("", tutor_required(views.BallotList.as_view()), name="ballot_list"),
    path("update/", tutorbest_required(views.BallotUpdate.as_view()), name="ballot_update"),
]
