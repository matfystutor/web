# vim:set fileencoding=utf-8:

from django import forms
from ..tutor.models import Tutor
from .models import ProfileActivation

class RegisterForm(forms.Form):
    studentnumber = forms.CharField(label="Årskortnummer")

    def clean_studentnumber(self):
        sn = self.cleaned_data['studentnumber']
        try:
            activation = ProfileActivation.objects.get(profile__studentnumber=sn)
        except ProfileActivation.DoesNotExist:
            raise forms.ValidationError('Dette årskortnummer har ingen udestående aktiveringer. Kontakt webfar@matfystutor.dk hvis du mener dette er en fejl.')
        if activation.profile.user is not None:
            raise forms.ValidationError('Din bruger er allerede aktiveret.')
        try:
            tutor = Tutor.objects.get(year=settings.YEAR, profile=activation.profile)
        except Tutor.DoesNotExist:
            raise forms.ValidationError('Du er ikke tutor i år.')
        return sn

class ActivateForm(forms.Form):
    username = forms.CharField(label="Brugernavn", required=True)
    pw = forms.CharField(label="Kodeord", widget=forms.PasswordInput, required=True)
    pw2 = forms.CharField(label="Kodeord (gentag)", widget=forms.PasswordInput, required=True)

    def clean_username(self):
        data = self.cleaned_data['username']
        if User.objects.filter(username=data).count() > 0:
            raise forms.ValidationError("Det brugernavn er allerede taget.")
        return data

    def clean_pw2(self):
        pw = self.cleaned_data['pw']
        data = self.cleaned_data['pw2']
        if pw != data:
            raise forms.ValidationError("Kodeordene stemmer ikke overens.")
        return data
