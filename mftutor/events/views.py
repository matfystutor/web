import re

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django.urls import reverse
from django.views.generic import DetailView, ListView, FormView, View

import mftutor.events.bulk
from mftutor.tutor.models import Tutor, TutorProfile
from mftutor.tutormail.views import EmailFormView
from .forms import RSVPForm, RSVPFormAjax, BulkImportForm, EventParticipantForm
from .models import Event, EventParticipant
from .. import settings


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

    return render(
        request,
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

    def render_to_response(self, context_data):
        response = (
            super(CalendarFeedView, self).render_to_response(context_data))
        response.render()
        content = response.content.decode("utf-8")
        # Break long lines
        content = re.sub(r'(.{74})(?=.)', r'\1\n ', content)
        # iCal requires CRLF line endings
        content = content.replace("\n", "\r\n")
        return HttpResponse(content, content_type='text/calendar')

    def get_context_data(self, **kwargs):
        d = super(CalendarFeedView, self).get_context_data(**kwargs)
        d['CALENDAR_NAME'] = settings.CALENDAR_NAME
        d['CALENDAR_DESCRIPTION'] = settings.CALENDAR_DESCRIPTION
        d['SITE_URL'] = settings.SITE_URL
        return d

    def get_queryset(self):
        qs = Event.objects.all()
        return qs.order_by('start_date')

class EventListView(ListView):
    def get_year(self):
        if 'year' in self.kwargs:
            return int(self.kwargs['year'])
        else:
            return self.request.year

    def get_queryset(self):
        qs = Event.objects.filter(start_date__year=self.get_year())
        return qs.order_by('start_date', 'start_time')

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
        d['specific_year'] = self.kwargs.get('year')
        if d['specific_year'] and not d['event_list']:
            raise Http404()
        d['year'] = self.get_year()
        d['years'] = [
            dt.year for dt in Event.objects.all().dates('start_date', 'year')
        ]
        return d

    template_name = "events.html"
    context_object_name = "event_list"

class RSVPFormView(FormView):
    form_class = RSVPFormAjax

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('events')

    def form_valid(self, form):
        event = Event.objects.get(pk__exact=self.kwargs['pk'])
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

    def get_rsvp(self):
        event = get_object_or_404(
            Event.objects.filter(pk=self.kwargs['event']))
        tutor = get_object_or_404(
            Tutor.objects.filter(pk=self.kwargs['tutor']))
        rsvp, created = EventParticipant.objects.get_or_create(
            event=event, tutor=tutor)
        return rsvp

    def get_context_data(self, **kwargs):
        rsvp = self.get_rsvp()
        self.initial = {
            'status': rsvp.status or 'none',
            'notes': rsvp.notes or '',
        }
        kwargs['rsvp'] = rsvp
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        rsvp = self.get_rsvp()
        return reverse('event_rsvps', kwargs={'pk': rsvp.event.pk})

    def form_valid(self, form):
        rsvp = self.get_rsvp()
        data = form.cleaned_data
        if data['status'] == 'none':
            rsvp.delete()
        else:
            rsvp.status = data['status']
            rsvp.notes = data['notes']
            rsvp.save()
        return super().form_valid(form)


class ReminderEmailView(EmailFormView):
    def get_event(self):
        return get_object_or_404(Event.objects.filter(pk=self.kwargs['pk']))

    def get_page_title(self):
        return 'Send reminder: %s' % self.get_event().title

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
        initial_data['subject'] = 'Husk tilmelding til %s!' % event.title
        initial_data['text'] = (
            'Kære tutorer!\n\n' +
            'Husk at tilmelde jer %s ' % event.title +
            'på tutorhjemmesiden:\n' +
            'http://matfystutor.dk/events/%s/\n' % event.pk
        )
        return initial_data
