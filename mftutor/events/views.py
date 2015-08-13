# vim:set fileencoding=utf-8:
from django.views.generic import DetailView, ListView, FormView, View
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponse
from .. import settings
from mftutor.tutor.models import Tutor, TutorProfile
from .models import Event, EventParticipant
from .forms import RSVPForm, RSVPFormAjax, BulkImportForm, EventParticipantForm
import mftutor.events.bulk

from mftutor.tutormail.views import EmailFormView

def event_detail_view(request, eventid):
    event = get_object_or_404(Event.objects.filter(pk=eventid))

    if request.tutor:
        try:
            instance = EventParticipant.objects.get(
                event=event, tutor=request.tutor)
        except EventParticipant.DoesNotExist:
            instance = EventParticipant()

        if request.method == 'POST':
            form = RSVPForm(
                data=request.POST, instance=instance,
                expect_event=event, expect_tutor=request.tutor)
            if form.is_valid():
                form.save()
        else:
            form = RSVPForm(instance=instance,
                            expect_event=event, expect_tutor=request.tutor)
    else:
        form = None

    rsvps = {p.tutor.pk: p for p in event.participants.all()}
    if event.rsvp != None:
        for tu in Tutor.members(request.year):
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
        qs = Event.objects.filter(start_date__year=self.request.year)
        return qs.order_by('start_date')

class EventListView(ListView):
    def get_queryset(self):
        qs = Event.objects.filter(start_date__year=self.request.year)
        return qs.order_by('start_date')

    def get_context_data(self, **kwargs):
        d = super(EventListView, self).get_context_data(**kwargs)
        for e in d['event_list']:
            e.rsvp_status = 'none'
            if self.request.tutor:
                try:
                    e.rsvp_status = EventParticipant.objects.get(
                        event=e, tutor=self.request.tutor).status
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
        event = Event.objects.get(pk__exact=self.args[0])
        try:
            ep = EventParticipant.objects.get(
                tutor=self.request.tutor, event=event)
        except EventParticipant.DoesNotExist:
            ep = EventParticipant(
                tutor=self.request.tutor, event=event)
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


class EventParticipantListView(DetailView):
    template_name = "event_rsvps.html"
    model = Event

    def get_context_data(self, **kwargs):
        context_data = (super(EventParticipantListView, self)
                        .get_context_data(**kwargs))
        event = context_data['event']
        participants = {p.tutor_id: p for p in event.participants.all()}
        names = {}
        tutors = {}
        for tutor in Tutor.members(self.request.year):
            names[tutor.pk] = tutor.profile.name
            tutors[tutor.pk] = participants.setdefault(
                tutor.pk, EventParticipant(event=event, tutor=tutor))
        tutors = sorted(tutors.values(), key=lambda o: names[o.tutor.pk])
        context_data['tutors'] = tutors
        return context_data


class EventParticipantEditView(FormView):
    template_name = "event_rsvp.html"
    form_class = EventParticipantForm

    def get_context_data(self, **kwargs):
        context_data = (super(EventParticipantEditView, self)
                        .get_context_data(**kwargs))
        event = get_object_or_404(
            Event.objects.filter(pk=self.kwargs['event']))
        tutor = get_object_or_404(
            Tutor.objects.filter(pk=self.kwargs['tutor']))
        rsvp, created = EventParticipant.objects.get_or_create(
            event=event, tutor=tutor)
        context_data['event'] = event
        context_data['tutor'] = tutor
        context_data['rsvp'] = rsvp
        return context_data

    def get_initial(self):
        context_data = self.get_context_data()
        return {
            'status': context_data['rsvp'].status or 'none',
            'notes': context_data['rsvp'].notes or '',
        }

    def get_success_url(self):
        context_data = self.get_context_data()
        return reverse('event_rsvps', kwargs={'pk': context_data['event'].pk})

    def form_valid(self, form):
        context_data = self.get_context_data()
        rsvp = context_data['rsvp']
        data = form.cleaned_data
        if data['status'] == 'none':
            rsvp.delete()
        else:
            rsvp.status = data['status']
            rsvp.notes = data['notes']
            rsvp.save()
        return super(EventParticipantEditView, self).form_valid(form)


class ReminderEmailView(EmailFormView):
    def get_event(self):
        return get_object_or_404(Event.objects.filter(pk=self.kwargs['pk']))

    def get_page_title(self):
        return u'Send reminder: %s' % self.get_event().title

    def get_recipients(self, form, year):
        event = self.get_event()
        profiles = TutorProfile.objects.filter(
            tutor__year__exact=year,
            tutor__early_termination__isnull=True)
        profiles = profiles.exclude(
            tutor__year__exact=year,
            tutor__events__event__pk=event.pk)
        return sorted([profile.email for profile in profiles])

    def get_initial(self):
        initial_data = super(ReminderEmailView, self).get_initial()
        event = self.get_event()
        initial_data['subject'] = u'Husk tilmelding til %s!' % event.title
        initial_data['text'] = (
            u'Kære tutorer!\n\n' +
            u'Husk at tilmelde jer %s ' % event.title +
            u'på tutorhjemmesiden:\n' +
            u'http://matfystutor.dk/events/%s/\n' % event.pk
        )
        return initial_data
