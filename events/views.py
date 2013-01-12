from django.views.generic import DetailView
from events.models import Event, EventParticipant
from django.forms import ModelForm
from tutor.auth import user_tutor_data
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

class RSVPForm(ModelForm):
    class Meta:
        model = EventParticipant
        fields = ('status', 'notes',)

    def clean(self):
        from django.core.exceptions import ValidationError

        res = super(RSVPForm, self).clean()

        self.instance.tutor = self.expect_tutor
        self.instance.event = self.expect_event

        return res

    def __init__(self, expect_event, expect_tutor, *args, **kwargs):
        super(RSVPForm, self).__init__(*args, **kwargs)
        self.expect_tutor = expect_tutor
        self.expect_event = expect_event

def event_detail_view(request, eventid):
    event = get_object_or_404(Event.objects.filter(pk=eventid))
    tutordata = user_tutor_data(request.user)
    if tutordata['err'] is None:
        tutor = tutordata['data']['tutor']

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
    else:
        form = None
    return render_to_response('event.html', {'event': event, 'rsvpform': form}, RequestContext(request))
