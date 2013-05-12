from django.views.generic import DetailView, ListView
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from ..tutor.auth import user_tutor_data, NotTutor
from .. import settings
from .models import Event, EventParticipant
from .forms import RSVPForm

def event_detail_view(request, eventid):
    event = get_object_or_404(Event.objects.filter(pk=eventid))
    try:
        tutordata = user_tutor_data(request.user)
        tutor = tutordata.tutor

        try:
            instance = EventParticipant.objects.get(event=event, tutor=tutor)
        except EventParticipant.DoesNotExist:
            instance = EventParticipant()

        if request.method == 'POST':
            form = RSVPForm(data=request.POST, instance=instance, expect_event=event, expect_tutor=tutor)
            if form.is_valid():
                form.save()
        else:
            form = RSVPForm(instance=instance, expect_event=event, expect_tutor=tutor)
    except NotTutor:
        form = None
    return render_to_response('event.html', {'event': event, 'rsvpform': form}, RequestContext(request))

class CalendarFeedView(ListView):
    model = Event
    template_name = 'ical.txt'

    def get_context_data(self, **kwargs):
        d = super(CalendarFeedView, self).get_context_data(**kwargs)
        d['CALENDAR_NAME'] = settings.CALENDAR_NAME
        d['CALENDAR_DESCRIPTION'] = settings.CALENDAR_DESCRIPTION
        d['SITE_URL'] = settings.SITE_URL
        return d

    def get_queryset(self):
        return Event.objects.filter(start_date__year=settings.YEAR).order_by('start_date')

class EventListView(ListView):
    def get_queryset(self):
        return Event.objects.filter(start_date__year=settings.YEAR).order_by('start_date')

    def get_context_data(self, **kwargs):
        d = super(EventListView, self).get_context_data(**kwargs)
        for e in d['event_list']:
            try:
                e.rsvp_status = EventParticipant.objects.get(
                    event=e, tutor__profile__user=self.request.user).status
            except EventParticipant.DoesNotExist:
                e.rsvp_status = 'none'
        return d

    template_name = "events.html"
    context_object_name = "event_list"
