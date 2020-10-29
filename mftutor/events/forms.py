from django import forms
from django.forms import Form, CharField, Textarea, ValidationError
from .models import EventParticipant
import mftutor.events.bulk


class RSVPForm(forms.ModelForm):
    class Meta:
        model = EventParticipant
        fields = ('status', 'notes',)

    def clean(self):
        res = super(RSVPForm, self).clean()

        self.instance.tutor = self.expect_tutor
        self.instance.event = self.expect_event

        return res

    def __init__(self, expect_event, expect_tutor, *args, **kwargs):
        super(RSVPForm, self).__init__(*args, **kwargs)
        self.expect_tutor = expect_tutor
        self.expect_event = expect_event


class RSVPFormAjax(forms.Form):
    status = forms.ChoiceField(choices=(
        ('yes', 'Kommer',),
        ('sandwich1', 'Lakse sandwich'),
        ('sandwich2', 'Italiensk pølse sandwich',),
        ('sandwich3', 'Kylling/bacon sandwich',),
        ('sandwich4', 'Roastbeef sandwich',),
        ('sandwich5', 'Vegansk sandwich',),
    ))


class BulkImportForm(Form):
    events = CharField(widget=Textarea)

    def clean_events(self):
        try:
            return mftutor.events.bulk.parse(self.cleaned_data['events'])
        except ValueError as e:
            raise ValidationError('Ugyldig data: %s' % e)


class EventParticipantForm(forms.Form):
    status = forms.ChoiceField(choices=(
        ('yes', 'Kommer'),
        ('no', 'Kommer ikke'),
        ('sandwich1', 'Lakse sandwich'),
        ('sandwich2', 'Italiensk pølse sandwich',),
        ('sandwich3', 'Kylling/bacon sandwich',),
        ('sandwich4', 'Roastbeef sandwich',),
        ('sandwich5', 'Vegansk sandwich',),
        ('none', 'Intet svar (slet notat)'),
    ))
    notes = forms.CharField(widget=forms.Textarea, required=False)
