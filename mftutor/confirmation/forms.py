# vim: set fileencoding=utf8:
from django import forms
from .models import Confirmation

class OwnConfirmationForm(forms.ModelForm):
    full_width_text_field = forms.TextInput(attrs={'style': 'width: 100%'})

    study = forms.CharField(widget=full_width_text_field, required=True,
            label='Studium samt sidefag/tilvalg')
    experience = forms.CharField(widget=full_width_text_field, required=True,
            label='I hvor mange år har du været holdtutor før i år?')
    priorities = forms.CharField(widget=full_width_text_field, required=True,
            label='Prioriteret rækkefølge af de seks studieretninger, du ønsker at være holdtutor for: Mat, møk, fys, nano, dat, it')
    firstaid = forms.CharField(widget=forms.Textarea, required=True,
            label='Har du førstehjælpsbevis eller førstehjælpskursus? Hvis ja, hvilket, og hvor gammelt er det?')
    resits = forms.CharField(widget=forms.Textarea, required=False,
            label='Har du reeksamener i rusugen? Hvis ja, hvilke og hvornår?')
    rusfriends = forms.CharField(widget=forms.Textarea, required=False,
            label='Kender du nogen studerende, der skal til at starte på mat/fys? Hvis ja, anfør navn og fag')
    comment = forms.CharField(widget=forms.Textarea, required=False,
            label='Kommentar')

    class Meta:
        fields = ('study', 'experience', 'priorities', 'firstaid', 'resits', 'rusfriends', 'comment')
        exclude = ('tutor', 'internal_notes')
        model = Confirmation

class EditNoteForm(forms.Form):
    tutor = forms.IntegerField(min_value=0)
    internal_notes = forms.CharField(required=False)

    class Meta:
        fields = ('tutor', 'internal_notes')
