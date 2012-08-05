# encoding: utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from tutor.models import Tutor, TutorProfile
from django.contrib.auth.views import password_change
from django import forms
from django.forms.extras import SelectDateWidget
from django.views.generic import ListView, UpdateView
from tutor.viewimpl.loginout import logout_view, login_view

class ProfileForm(forms.Form):
    first_name = forms.CharField(label='Fornavn')
    last_name = forms.CharField(label='Efternavn')
    street = forms.CharField(label='Gade')
    city = forms.CharField(label='Postnr. og by')
    phone = forms.CharField(label='Telefon')
    email = forms.EmailField(label='Email')
    study = forms.CharField(label='Studium')
    studentnumber = forms.CharField(label='Årskortnummer')
    birthday = forms.DateField(label='Fødselsdag', widget=SelectDateWidget(years=range(1970,2012)))
    gender = forms.ChoiceField(choices=(('m', 'Mand',), ('f', 'Kvinde',),),label='Køn')

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
            tp.studentnumber = form.cleaned_data['studentnumber']
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

    return render(request, 'profile.html', { 'form': form, })

class GroupsView(ListView):
    context_object_name = 'groups'
    template_name = 'groups.html'
    def get_queryset(self):
        return Tutor.objects.get(profile=self.request.user.get_profile(), year=2012).groups.all()

def tutor_password_change_view(request):
    if 'back' in request.GET:
        back = request.GET['back']
    else:
        back = reverse('news')
    return password_change(request, 'registration/password_change_form.html', back)

class UploadPictureForm(forms.ModelForm):
    class Meta:
        model = TutorProfile
        fields = ('picture',)

class UploadPictureView(UpdateView):
    model = TutorProfile
    template_name = 'uploadpicture.html'
    form_class = UploadPictureForm
    def get_object(self):
        return self.request.user.get_profile()
    def get_success_url(self):
        return reverse('upload_picture_view')
