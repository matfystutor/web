from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
from tutor.models import Tutor
from tutor.views import logout_view, login_view
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^tutors/$', login_required(
        ListView.as_view(
            queryset=Tutor.objects.filter(year=2012, early_termination__isnull=True),
            template_name="tutors.html",
            context_object_name="tutor_list")),
        name='tutors'),
    url(r'^logout/$', logout_view),
    url(r'^login/$', login_view),
    url(r'^login/\?err=(?P<err>.*)$', login_view, name='login_error'),
)
