# vim: set fileencoding=utf8:
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, get_list_or_404
from django import forms
from django.db.models import Count

from ..tutor.models import TutorProfile, RusClass, TutorGroup, Tutor

class ProfileView(TemplateView):
    template_name = 'browser/profile.html'

    def get_context_data(self, **kwargs):
        context_data = super(ProfileView, self).get_context_data(**kwargs)
        tp = get_object_or_404(TutorProfile, studentnumber=self.kwargs['studentnumber'])
        context_data['subject'] = tp
        years = []
        for tutor in tp.tutor_set.all().select_related('profile__tutor'):
            years.append({'year': tutor.year, 'tutor': tutor})
        for rus in tp.rus_set.all().select_related('profile__tutor'):
            years.append({'year': rus.year, 'rus': rus})
        context_data['years'] = sorted(years, key=lambda y: y['year'])
        return context_data

class RusClassView(TemplateView):
    template_name = 'browser/rusclass.html'

    def get_context_data(self, **kwargs):
        context_data = super(RusClassView, self).get_context_data(**kwargs)
        context_data['rusclass'] = get_object_or_404(RusClass, year=self.kwargs['year'], handle=self.kwargs['handle'])
        return context_data

class GroupView(TemplateView):
    template_name = 'browser/group.html'

    def get_context_data(self, **kwargs):
        context_data = super(GroupView, self).get_context_data(**kwargs)
        context_data['year'] = self.kwargs['year']
        group = context_data['group'] = get_object_or_404(TutorGroup, handle=self.kwargs['handle'])
        context_data['members'] = get_list_or_404(Tutor, year=self.kwargs['year'], groups=group)
        return context_data

class SearchForm(forms.Form):
    query = forms.CharField()
    tutors_only = forms.BooleanField(required=False, initial=True)

class SearchView(TemplateView):
    template_name = 'browser/search.html'

    def get_context_data(self, **kwargs):
        context_data = super(SearchView, self).get_context_data(**kwargs)
        form = SearchForm(self.request.GET)
        if form.is_valid():
            query = context_data['query'] = form.cleaned_data['query']
            if form.cleaned_data['tutors_only']:
                context_data['results'] = (
                        TutorProfile.objects.filter(name__icontains=query)
                        .annotate(tutor_count=Count('tutor'))
                        .filter(tutor_count__gt=0))
            else:
                context_data['results'] = TutorProfile.objects.filter(name__icontains=query)[0:30]
        else:
            form = SearchForm()
        context_data['form'] = form
        return context_data
