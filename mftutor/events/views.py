from django.views.generic import DetailView, ListView, FormView
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponse
from ..tutor.auth import user_tutor_data, NotTutor
from .. import settings
from .models import Event, EventParticipant
from .forms import RSVPForm, RSVPFormAjax

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

class RSVPFormView(FormView):
    form_class = RSVPFormAjax

    def get_success_url(self):
        return reverse('events')

    def form_valid(self, form):
        tutordata = user_tutor_data(self.request.user)
        event = Event.objects.get(pk__exact=self.args[0])
        try:
            ep = EventParticipant.objects.get(tutor=tutordata.tutor, event=event)
        except EventParticipant.DoesNotExist:
            ep = EventParticipant(tutor=tutordata.tutor, event=event)
        ep.status = form.cleaned_data['status']
        ep.save()

        return HttpResponse(status=204)
