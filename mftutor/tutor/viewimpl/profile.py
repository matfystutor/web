# encoding: utf-8
from django import forms
from django.forms.extras import SelectDateWidget
from django.shortcuts import render, redirect
from django.contrib.sites.models import get_current_site
from django.views.generic import FormView
from ...settings import YEAR
from ..auth import user_tutor_data

class ProfileForm(forms.Form):
    name = forms.CharField(label='Navn')
    street = forms.CharField(label='Gade')
    city = forms.CharField(label='Postnr. og by')
    phone = forms.CharField(label='Telefon')
    email = forms.EmailField(label='Email')
    study = forms.CharField(label='Studium')
    birthday = forms.DateField(label='Fødselsdag', widget=SelectDateWidget(years=range(1970,YEAR)))

class ProfileView(FormView):
    form_class = ProfileForm
    template_name = 'profile.html'

    def dispatch(self, request):
        d = user_tutor_data(request.user)
        self.tutorprofile = d.profile
        return super(ProfileView, self).dispatch(request)

    def get_context_data(self, **kwargs):
        context_data = super(ProfileView, self).get_context_data(**kwargs)
        context_data['studentnumber'] = self.tutorprofile.studentnumber
        return context_data

    def get_initial(self):
        tp = self.tutorprofile
        return {
                'name': tp.name,
                'street': tp.street,
                'city': tp.city,
                'phone': tp.phone,
                'email': tp.email,
                'study': tp.study,
                'birthday': tp.birthday,
                }

    def form_valid(self, form):
        tp = self.tutorprofile
        u = tp.user
        tp.name = form.cleaned_data['name']
        if ' ' in tp.name:
            first_name, last_name = tp.name.split(' ', 1)
        else:
            first_name = tp.name
            last_name = ''
        u.first_name = first_name
        u.last_name = last_name
        tp.street = form.cleaned_data['street']
        tp.city = form.cleaned_data['city']
        tp.phone = form.cleaned_data['phone']
        u.email = tp.email = form.cleaned_data['email']
        tp.study = form.cleaned_data['study']
        tp.birthday = form.cleaned_data['birthday']
        u.save()
        tp.save()
        return self.render_to_response(self.get_context_data(form=form, saved=True))

profile_view = ProfileView.as_view()
