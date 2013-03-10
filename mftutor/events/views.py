from django.views.generic import DetailView
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from ..tutor.auth import user_tutor_data, NotTutor
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
