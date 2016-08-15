# encoding: utf-8
from django import forms
from django.views.generic import FormView
from django.core.exceptions import ValidationError


class ProfileForm(forms.Form):
    name = forms.CharField(label='Navn')
    street = forms.CharField(label='Gade')
    city = forms.CharField(label='Postnr. og by')
    phone = forms.CharField(label='Telefon')
    email = forms.EmailField(label='Email')
    study = forms.CharField(label='Studium')


class ProfileView(FormView):
    form_class = ProfileForm
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context_data = super(ProfileView, self).get_context_data(**kwargs)
        context_data['studentnumber'] = self.request.tutorprofile.studentnumber
        return context_data

    def get_initial(self):
        tp = self.request.tutorprofile
        return {
            'name': tp.name,
            'street': tp.street,
            'city': tp.city,
            'phone': tp.phone,
            'email': tp.email,
            'study': tp.study,
        }

    def form_valid(self, form):
        tp = self.request.tutorprofile
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
        try:
            tp.full_clean()
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        u.save()
        tp.save()

        # Since TutorProfile cleaning may have changed tp.phone,
        # throw away the bound form and recreate it with the profile data
        form = self.get_form_class()(initial=self.get_initial())
        return self.render_to_response(
            self.get_context_data(form=form, saved=True))

profile_view = ProfileView.as_view()
