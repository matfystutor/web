# vim: set fileencoding=utf8:
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django import forms
from django.views.generic import UpdateView, TemplateView, View
from django.views.generic.edit import FormMixin
from django.http import HttpResponseRedirect

from ..tutor.auth import tutorbest_required_error, tutor_required_error
from mftutor.tutor.models import Tutor, TutorProfile
from mftutor.tutormail.views import EmailFormView
from .models import Confirmation
from .forms import OwnConfirmationForm, EditNoteForm


def parse_study(study):
    """
    >>> parse_study('Plantefysiker')
    fys
    >>> parse_study('Astro')
    fys
    >>> parse_study(' Mat/fys')
    mat
    >>> parse_study('Fys/mat')
    fys
    >>> parse_study('Fys med mat sidefag')
    fys
    """

    study = study.lower().strip()
    if study.startswith('mat'):
        if 'øk' in study or 'ok' in study:
            return 'mok'
        else:
            return 'mat'
    elif study.startswith('fys'):
        return 'fys'
    elif study.startswith('it'):
        return 'it'
    elif study.startswith('dat'):
        return 'dat'
    elif study.startswith('nano'):
        return 'nano'
    elif 'øk' in study or 'ok' in study:
        return 'mok'
    elif 'fys' in study or 'astro' in study:
        return 'fys'
    elif 'dat' in study or 'web' in study:
        return 'dat'
    elif 'mat' in study:
        return 'mat'
    elif 'nano' in study:
        return 'nano'
    elif 'it' in study:
        return 'it'
    else:
        return None


class OwnConfirmationView(UpdateView):
    form_class = OwnConfirmationForm

    def dispatch(self, request, *args, **kwargs):
        if not request.tutor:
            return tutor_required_error(request)

        return super(OwnConfirmationView, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        try:
            return Confirmation.objects.get(tutor=self.request.tutor)
        except Confirmation.DoesNotExist:
            return Confirmation(tutor=self.request.tutor, study=self.request.tutorprofile.study)

    def form_valid(self, form):
        if self.object.tutor != self.request.tutor:
            errors = form._errors.setdefault(forms.forms.NON_FIELD_ERRORS, forms.util.ErrorList())
            errors.append(u"Ugyldig tutor")
            return self.form_invalid(form)

        self.object = form.save(commit=False)
        self.object.save()

        return self.render_to_response(self.get_context_data(object=self.object, form=form, success=True))

class ConfirmationListView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(ConfirmationListView, self).get_context_data(**kwargs)
        members = Tutor.members(self.request.year)
        members = members.select_related('confirmation')
        confirmations = []
        for t in members:
            try:
                c = t.confirmation
                c.study_short = parse_study(c.study)
                confirmations.append(c)
            except Confirmation.DoesNotExist:
                confirmations.append(Confirmation(tutor=t))
        context['confirmation_list'] = sorted(
            confirmations,
            key=lambda c: c.tutor.profile.get_full_name())
        return context

class ConfirmationTableView(ConfirmationListView):
    template_name = 'confirmation/confirmation_table.html'

class ConfirmationCardView(ConfirmationListView):
    template_name = 'confirmation/confirmation_card.html'

class EditNoteView(View, FormMixin):
    model = Confirmation
    form_class = EditNoteForm

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('confirmation_table')

    def form_valid(self, form):
        try:
            c = Confirmation.objects.get(tutor__pk__exact=form.cleaned_data['tutor'])
        except Confirmation.DoesNotExist:
            c = Confirmation(tutor=Tutor.objects.get(pk__exact=form.cleaned_data['tutor']))
        c.internal_notes = form.cleaned_data['internal_notes']
        c.save()
        url = '%s#confirmation_%s' % (self.get_success_url(), c.pk)
        return HttpResponseRedirect(url)

    def dispatch(self, request, *args, **kwargs):
        if not request.tutor:
            return tutorbest_required_error(request)
        if not request.tutor.is_tutorbest():
            return tutorbest_required_error(request)

        return super(EditNoteView, self).dispatch(request, *args, **kwargs)


class ReminderEmailView(EmailFormView):
    def get_page_title(self):
        return u'Send reminder om tutorbekræftelsen'

    def get_recipients(self, form, year):
        profiles = TutorProfile.objects.filter(
            tutor__year__exact=year,
            tutor__early_termination__isnull=True)
        profiles = profiles.exclude(
            tutor__year__exact=year,
            tutor__confirmation__pk__gt=0)
        return sorted([profile.email for profile in profiles])

    def get_initial(self):
        initial_data = super(ReminderEmailView, self).get_initial()
        initial_data['subject'] = u'Husk at udfylde tutorbekræftelsen!'
        initial_data['text'] = (
            u'Kære tutorer!\n\n' +
            u'Husk at besvare tutorbekræftelsen ' +
            u'på tutorhjemmesiden:\n' +
            u'http://matfystutor.dk/confirmation/\n'
        )
        return initial_data
