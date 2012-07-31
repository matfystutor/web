from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
from tutor.models import Tutor
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^tutors/$', login_required(
        ListView.as_view(
            queryset=Tutor.objects.filter(year=2012, early_termination__isnull=True),
            template_name="tutors.html",
            context_object_name="tutor_list"))),
)
