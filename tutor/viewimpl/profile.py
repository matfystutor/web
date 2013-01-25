# encoding: utf-8
from django import forms
from django.forms.extras import SelectDateWidget
from django.shortcuts import render, redirect
from mftutor.settings import YEAR
from django.contrib.sites.models import get_current_site

# ReadOnlyWidget and Field
# http://lazypython.blogspot.dk/2008/12/building-read-only-field-in-django.html
# Tommi Penttinen, May 19, 2009 at 10:28 AM
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.forms.util import flatatt

class ReadOnlyWidget(forms.Widget):
    def render(self, name, value, attrs):
        final_attrs = self.build_attrs(attrs, name=name)
        if hasattr(self, 'initial'):
            value = self.initial
        return unicode(value)

    def _has_changed(self, initial, data):
        return False

class ReadOnlyField(forms.Field):
    widget = ReadOnlyWidget
    def __init__(self, widget=None, label=None, initial=None, help_text=None):
        super(type(self), self).__init__(self, label=label, initial=initial,
            help_text=help_text, widget=widget)
        self.widget.initial = initial

    def clean(self, value):
        return self.widget.initial


class ProfileForm(forms.Form):
    first_name = forms.CharField(label='Fornavn')
    last_name = forms.CharField(label='Efternavn')
    street = forms.CharField(label='Gade')
    city = forms.CharField(label='Postnr. og by')
    phone = forms.CharField(label='Telefon')
    email = forms.EmailField(label='Email')
    study = forms.CharField(label='Studium')
    studentnumber = ReadOnlyField(label='Årskortnummer')
    birthday = forms.DateField(label='Fødselsdag', widget=SelectDateWidget(years=range(1970,YEAR)))
    gender = forms.ChoiceField(widget=forms.RadioSelect, choices=(('m', 'Mand',), ('f', 'Kvinde',),),label='Køn')

def profile_view(request):
    u = request.user
    tp = u.get_profile()
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            u.first_name = form.cleaned_data['first_name']
            u.last_name = form.cleaned_data['last_name']
            tp.street = form.cleaned_data['street']
            tp.city = form.cleaned_data['city']
            tp.phone = form.cleaned_data['phone']
            u.email = form.cleaned_data['email']
            tp.study = form.cleaned_data['study']
            #tp.studentnumber = form.cleaned_data['studentnumber']
            tp.birthday = form.cleaned_data['birthday']
            tp.gender = form.cleaned_data['gender']
            u.save()
            tp.save()
            return redirect('profile_view')
    else:
        initial = {
            'first_name': u.first_name,
            'last_name': u.last_name,
            'street': tp.street,
            'city': tp.city,
            'phone': tp.phone,
            'email': u.email,
            'study': tp.study,
            'studentnumber': tp.studentnumber,
            'birthday': tp.birthday,
            'gender': tp.gender,
        }
        form = ProfileForm(initial=initial)

    form.fields['studentnumber'].widget.initial = tp.studentnumber
    return render(request, 'profile.html', {'form': form})
