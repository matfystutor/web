from django.views.generic import DetailView, ListView, FormView, View
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponse
from ..tutor.auth import user_tutor_data, NotTutor
from .. import settings
from mftutor.tutor.models import Tutor
from .models import Event, EventParticipant
from .forms import RSVPForm, RSVPFormAjax, BulkImportForm
import mftutor.events.bulk

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

    rsvps = {p.tutor.pk: p for p in event.participants.all()}
    if event.rsvp != None:
        for tu in Tutor.members.all():
            rsvps.setdefault(tu.pk, EventParticipant(tutor=tu))
    accept = []
    decline = []
    no_answer = []
    for rsvp in rsvps.values():
        if rsvp.status == 'yes':
            accept.append(rsvp.tutor)
        elif rsvp.status == 'no':
            decline.append(rsvp.tutor)
        else:
            no_answer.append(rsvp.tutor)
    accept.sort(key=lambda tu: tu.profile.name)
    decline.sort(key=lambda tu: tu.profile.name)
    no_answer.sort(key=lambda tu: tu.profile.name)

    return render_to_response(
        'event.html',
        {
            'event': event,
            'rsvpform': form,
            'accept': accept,
            'decline': decline,
            'no_answer': no_answer,
        },
        RequestContext(request),
    )

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
        try:
            tutordata = user_tutor_data(self.request.user)
        except NotTutor:
            tutordata = None
        for e in d['event_list']:
            e.rsvp_status = 'none'
            if tutordata:
                try:
                    e.rsvp_status = EventParticipant.objects.get(
                        event=e, tutor=tutordata.tutor).status
                except EventParticipant.DoesNotExist:
                    pass
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


class BulkExportView(View):
    def get(self, request, year):
        events = (
            Event.objects.filter(start_date__year=year).order_by('start_date'))

        return HttpResponse(
            content=mftutor.events.bulk.dumps(events),
            mimetype='text/plain; charset=utf8',
        )


class BulkImportView(FormView):
    form_class = BulkImportForm
    template_name = "events_import.html"

    def get_success_url(self):
        return reverse('events_import')

    def form_valid(self, form):
        for event in form.cleaned_data['events']:
            event.save()
        return super(BulkImportView, self).form_valid(form)
