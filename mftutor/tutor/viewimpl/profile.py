# encoding: utf-8
from django import forms
from django.views.generic import FormView
from django.core.exceptions import ValidationError

from mftutor import settings
from mftutor.settings import STUDIES
from mftutor.shirt.models import ShirtPreference
from mftutor.shirt.views import SelectShirt
from mftutor.tutor.managers import TutorManager
from mftutor.tutor.models import Tutor, TutorGroup

class ProfileForm(forms.Form):
    name = forms.CharField(label='Navn')
    nickname = forms.CharField(label='Kaldenavn', required=False)
    street = forms.CharField(label='Gade')
    city = forms.CharField(label='Postnr. og by')
    phone = forms.CharField(label='Telefon')
    email = forms.EmailField(label='Email')
    study = forms.ChoiceField(label='Studium', choices=[(s, s) for s in STUDIES], required=False)
    tshirt1 = forms.CharField(widget=SelectShirt, label='T-Shirt Størrelse 1')
    tshirt2 = forms.CharField(widget=SelectShirt, label='T-Shirt Størrelse 2')
    burBrevSignup = forms.BooleanField(label='Tilmed Burets Nyhedsbrev', required=False)
    picture = forms.ImageField(
        required=False,
        label='Billede')


class ProfileView(FormView):
    form_class = ProfileForm
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context_data = super(ProfileView, self).get_context_data(**kwargs)
        context_data['studentnumber'] = self.request.tutorprofile.studentnumber
        context_data['picture'] = self.request.tutorprofile.picture
        return context_data

    def get_initial(self):
        tp = self.request.tutorprofile
        try:
            sp = ShirtPreference.objects.get(profile=tp)
        except ShirtPreference.DoesNotExist:
            sp = ShirtPreference(profile=tp)
            sp.save()
        return {
            'name': tp.name,
            'nickname': tp.nickname,
            'street': tp.street,
            'city': tp.city,
            'phone': tp.phone,
            'email': tp.email,
            'study': tp.study,
            'tshirt1': sp.choice1,
            'tshirt2': sp.choice2,
            'burBrevSignup': tp.burBrevSignup
        }

    def form_valid(self, form):
        tp = self.request.tutorprofile
        sp = ShirtPreference.objects.get(profile=tp)
        u = tp.user
        tp.name = form.cleaned_data['name']
        if ' ' in tp.name:
            first_name, last_name = tp.name.split(' ', 1)
        else:
            first_name = tp.name
            last_name = ''
        u.first_name = first_name
        u.last_name = last_name
        tp.nickname = form.cleaned_data['nickname']
        tp.street = form.cleaned_data['street']
        tp.city = form.cleaned_data['city']
        tp.phone = form.cleaned_data['phone']
        u.email = tp.email = form.cleaned_data['email']

        tp.study = form.cleaned_data['study']

        tp.burBrevSignup = form.cleaned_data['burBrevSignup']

        sp.choice1 = form.cleaned_data['tshirt1']
        sp.choice2 = form.cleaned_data['tshirt2']

        picture_data = form.cleaned_data['picture']
        if picture_data is not None:
            tp.picture = picture_data

        try:
            tp.full_clean()
            sp.full_clean()
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        u.save()
        tp.save()
        sp.save()

        # Add profile to burbrev if set
        tutorManager = Tutor.objects.all()
        groupManager = TutorGroup.objects.all()

        try :
            burBrevGroup = groupManager.get(handle="burbrev", year=settings.TUTORMAIL_YEAR)
            tutor = tutorManager.get(profile=tp, year=settings.TUTORMAIL_YEAR)
            if tp.burBrevSignup is True:
                tutor.groups.add(burBrevGroup)   
            else:
                tutor.groups.remove(burBrevGroup)
        except:
            pass
        
        # Since TutorProfile cleaning may have changed tp.phone,
        # throw away the bound form and recreate it with the profile data
        form = self.get_form_class()(initial=self.get_initial())
        return self.render_to_response(
            self.get_context_data(form=form, saved=True))

profile_view = ProfileView.as_view()
