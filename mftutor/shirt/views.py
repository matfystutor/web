# vim: set fileencoding=utf8:
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect, render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.views.generic import FormView, UpdateView, TemplateView

#from ..settings import YEAR
from .models import ShirtOption, ShirtPreference
from mftutor.tutor.models import Tutor

class ShirtOptionForm(forms.Form):
    choices = forms.CharField(widget=forms.Textarea)

class ShirtOptionView(FormView):
    form_class = ShirtOptionForm
    template_name = 'shirt/shirtoptions_form.html'

    def get_initial(self):
        choices = []
        for so in ShirtOption.objects.all():
            choices.append(so.choice)
        return {'choices':
                u'\n'.join(choices)}

    def get_success_url(self):
        return reverse('shirt_options')

    def form_valid(self, form):
        choices = []
        pos = 1
        for c in form.cleaned_data['choices'].replace('\r', '').split('\n'):
            choices.append({'choice': c, 'position': pos})
            pos = pos + 1
        ShirtOption.objects.all().delete()
        for c in choices:
            ShirtOption(**c).save()
        return super(ShirtOptionView, self).form_valid(form)

class SelectShirt(forms.Select):
    def render(self, *args, **kwargs):
        choices = [(so.choice, so.choice) for so in ShirtOption.objects.all()]
        kwargs.update({'choices': choices})
        return super(SelectShirt, self).render(*args, **kwargs)

class ShirtPreferenceForm(forms.ModelForm):
    choice1 = forms.CharField(widget=SelectShirt, label='T-shirt 1')
    choice2 = forms.CharField(widget=SelectShirt, label='T-shirt 2')

    def clean_choice_generic(self, field):
        data = self.cleaned_data[field]
        if ShirtOption.objects.filter(choice__exact=data).count() == 0:
            raise forms.ValidationError(u'Ugyldig størrelse')
        return data

    def clean_choice1(self):
        return self.clean_choice_generic('choice1')

    def clean_choice2(self):
        return self.clean_choice_generic('choice2')

    class Meta:
        model = ShirtPreference
        fields = ('choice1', 'choice2')

class ShirtPreferenceView(UpdateView):
    model = ShirtPreference
    form_class = ShirtPreferenceForm

    def get_success_url(self):
        return reverse('shirt_preference')

    def get_object(self):
        try:
            return ShirtPreference.objects.get(profile=self.request.user.tutorprofile)
        except ShirtPreference.DoesNotExist:
            sp = ShirtPreference(profile=self.request.user.tutorprofile)
            sp.save()
            return sp


class ShirtChoicesView(TemplateView):
    template_name = 'shirt/shirtchoices.html'

    def get_tutors(self):
        tutors = list(Tutor.members(self.request.year))
        sp = ShirtPreference.objects.filter(profile__tutor__in=tutors)
        sp_dict = {s.profile.pk: s for s in sp}
        for tu in tutors:
            try:
                s = sp_dict[tu.profile.pk]
            except KeyError:
                s = ShirtPreference()
            tu.choice1 = s.choice1
            tu.choice2 = s.choice2
            tu.choice_created = s.created
            tu.choice_updated = s.updated
        tutors.sort(key=lambda tu: (0, tu.profile.name) if tu.choice_updated is None or tu.choice1 in ('', 'Ingen') else (1, tu.choice_updated))
        return tutors

    def get_context_data(self, **kwargs):
        data = super(ShirtChoicesView, self).get_context_data(**kwargs)
        data['tutors'] = self.get_tutors()
        return data
