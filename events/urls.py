from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
from tutor.models import Tutor, TutorGroup, BoardMember
from events.models import Event
from django.contrib.auth.decorators import login_required
from events.views import *
from mftutor.settings import siteconfig

urlpatterns = patterns('',
    url(r'^$',
        ListView.as_view(
            queryset=Event.objects.filter(start_date__year=siteconfig.year).order_by('start_date'),
            template_name="events.html",
            context_object_name="event_list"),
        name="events"),
    url(r'^(\d+)/$',
        event_detail_view,
        name="event"),
)
