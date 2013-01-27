# vim:set fileencoding=utf-8:
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import RequestContext
from django import forms
from django.forms import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from activation.models import ProfileActivation
from mftutor import settings
from tutor.models import Tutor

class RegisterForm(forms.Form):
    studentnumber = forms.CharField(label="Årskortnummer")

    def clean_studentnumber(self):
        sn = self.cleaned_data['studentnumber']
        try:
            activation = ProfileActivation.objects.get(profile__studentnumber=sn)
        except ProfileActivation.DoesNotExist:
            raise ValidationError('Dette årskortnummer har ingen udestående aktiveringer. Kontakt webfar@matfystutor.dk hvis du mener dette er en fejl.')
        if activation.profile.user is not None:
            raise ValidationError('Din bruger er allerede aktiveret.')
        try:
            tutor = Tutor.objects.get(year=settings.YEAR, profile=activation.profile)
        except Tutor.DoesNotExist:
            raise ValidationError('Du er ikke tutor i år.')
        return sn

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            activation = ProfileActivation.objects.get(profile__studentnumber=form.cleaned_data['studentnumber'])
            activation.generate_new_key()
            from django.contrib.sites.models import get_current_site
            domain = get_current_site(request).domain
            mail = activation.generate_mail(domain)
            if settings.ACTIVATION_DEBUG:
                txt = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (mail.from_email, mail.to, mail.subject, mail.body)
                return HttpResponse(txt, content_type='text/plain')
            else:
                mail.send()
                return HttpResponseRedirect(reverse('activation_thanks'))
    else:
        form = RegisterForm()
    return render(request, 'activation/register.html', {'form': form})

class ActivateForm(forms.Form):
    username = forms.CharField(label="Brugernavn", required=True)
    pw = forms.CharField(label="Kodeord", widget=forms.PasswordInput, required=True)
    pw2 = forms.CharField(label="Kodeord (gentag)", widget=forms.PasswordInput, required=True)

    def clean_username(self):
        data = self.cleaned_data['username']
        if User.objects.filter(username=data).count() > 0:
            raise ValidationError("Det brugernavn er allerede taget.")
        return data

    def clean_pw2(self):
        pw = self.cleaned_data['pw']
        data = self.cleaned_data['pw2']
        if pw != data:
            raise ValidationError("Kodeordene stemmer ikke overens.")
        return data

def activate_view(request, activation_key):
    activation = get_object_or_404(ProfileActivation, activation_key=activation_key)
    if activation.profile.user:
        return render(request, 'activation/already_activated.html', {}, status=403)
    if request.method == 'POST':
        form = ActivateForm(request.POST)
        if form.is_valid():
            user = User(username=form.cleaned_data['username'],
                    first_name=activation.first_name,
                    last_name=activation.last_name,
                    email=activation.email)
            user.set_password(form.cleaned_data['pw'])
            user.save()
            activation.profile.user = user
            activation.profile.save()
            return HttpResponseRedirect(reverse('activation_activated'))
    else:
        form = ActivateForm(initial={'username': activation.profile.studentnumber})
    return render(request, 'activation/activate.html', {'form': form})
