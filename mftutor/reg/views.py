# vim: set fileencoding=utf8:
import re
import copy
import json
import random
import string
import datetime
import subprocess

from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django import forms
from django.views.generic import (
    ListView, FormView, UpdateView, TemplateView, View)
from django.views.generic.edit import ProcessFormView
from django.contrib.auth.models import User

from .. import settings
from ..tutor.models import RusClass, TutorProfile, Rus
from mftutor.tutor.auth import (
    tutor_required_error, rusclass_required_error, tutorbest_required_error)

from mftutor.reg.models import (
    ImportSession, ImportLine, Note, ChangeLogEntry, Handout,
    HandoutRusResponse, HandoutClassResponse)
from .models import LightboxRusClassState, LightboxNote
from .email import make_password_reset_message, send_messages


# =============================================================================

class BurStartView(TemplateView):
    template_name = 'reg/bur_start.html'


# =============================================================================

class ChooseSessionView(ListView):
    model = ImportSession

    def get_queryset(self):
        return ImportSession.objects.filter(year__exact=self.request.year)


class NewSessionView(ProcessFormView):
    """POST target used by ChooseSessionView to create a new ImportSession."""

    def post(self, request):
        importsession = ImportSession(
            year=request.year, author=request.user.tutorprofile)
        importsession.save()
        return HttpResponseRedirect(
            reverse('import_session_edit', kwargs={'pk': importsession.pk}))


class EditSessionForm(forms.ModelForm):
    class Meta:
        model = ImportSession
        fields = ('year', 'name', 'regex', 'author')

    year = forms.CharField(required=False)
    author = forms.CharField(required=False)
    imported = forms.CharField(required=False)

    regex = forms.CharField()
    name = forms.CharField()
    lines = forms.CharField(widget=forms.Textarea)

    empty_initial_rusclass = forms.BooleanField(required=False)

    def clean_regex(self):
        """Check if regex is valid by compiling it.

        Later on, clean() then checks if the regex matches useful things."""

        data = self.cleaned_data['regex']
        try:
            re.compile(data)
        except re.error as v:
            e = forms.ValidationError("Fejl i regulært udtryk: %s" % (v,))
            self.add_error('regex', e)
            return

        return data

    def clean_year(self):
        """Read-only model field as far as this form is concerned."""
        return self.instance.year

    def clean_author(self):
        """Read-only model field as far as this form is concerned."""
        return self.instance.author

    def clean_imported(self):
        """Read-only model field as far as this form is concerned."""
        return self.instance.imported

    def clean(self):
        """Check if regex matches the lines and yields the right capture
        groups.

        It is expected to yield just the named groups specified by `expected`.

        It is not expected to yield any other named groups, or any numbered
        groups.
        """

        cleaned_data = super(EditSessionForm, self).clean()

        regex = cleaned_data.get('regex')
        lines = cleaned_data.get('lines')

        # Named groups we expect in the input
        expected = frozenset(('rusclass', 'name', 'studentnumber'))
        expected_string = ', '.join('(?P<'+k+'>...)' for k in expected) + '.'

        if regex and lines:
            r = re.compile(regex)
            matches = 0
            linecount = 0
            for line in lines.splitlines():
                linecount = linecount + 1
                m = r.match(line)
                if m:
                    matches = matches + 1
                    groups = m.groups()
                    groupdict = m.groupdict()
                    # `groups` contains both named and numbered match groups;
                    # `groupdict` contains only named match groups.
                    # We only want named match groups.
                    if len(groups) != len(groupdict):
                        e = forms.ValidationError(
                            ("Det regulære udtryk matcher UNAVNGIVNE " +
                             "grupper. Brug kun navngivne grupper %s") %
                            (expected_string,))
                        self.add_error('regex', e)
                        return
                    groupkeys = frozenset(groupdict.keys())
                    if not groupkeys.issubset(expected):
                        e = forms.ValidationError(
                            ("Det regulære udtryk matcher UKENDTE " +
                             "gruppenavne. Brug kun navngivne grupper %s") %
                            (expected_string,))
                        self.add_error('regex', e)
                        return
                    if not expected.issubset(groupkeys):
                        e = forms.ValidationError(
                            ("Det regulære udtryk matcher IKKE " +
                             "alle de navngivne grupper %s") %
                            (expected_string,))
                        self.add_error('regex', e)
                        return

                    for n, v in groupdict.items():
                        if v == '':
                            e = forms.ValidationError(
                                ("Det regulære udtryk matcher gruppen '%s' " +
                                 "som den tomme streng.") % (n,))
                            self.add_error('regex', e)
                            return

            if matches == 0:
                e = forms.ValidationError(
                    "Det regulære udtryk matcher ingen strenge i input.")
                self.add_error('regex', e)
                return

        return cleaned_data


class EditSessionView(UpdateView):
    """An import session hits the EditSessionView multiple times.

    First, the NewSessionView redirects the user to an empty ImportSession.
    The user inputs a regular expression and a bunch of lines and submits.
    Then, this view matches the regex against the lines and saves the result
    as ImportLines and displays them to the user.

    If the user then wants to create the appropriate Rus and RusClass objects,
    he clicks the submit button named "create"."""
    form_class = EditSessionForm
    template_name = 'reg/edit_session_form.html'

    def get_form(self, form_class=None):
        form = super(EditSessionView, self).get_form(form_class)
        if form.instance and form.instance.pk is not None:
            qs = ImportLine.objects.filter(session=form.instance)
            lines = '\n'.join(il.line for il in qs.order_by('position'))
            form.fields['lines'].initial = lines
        return form

    def get_object(self):
        return ImportSession.objects.get(pk=self.kwargs.get('pk'))

    def get_context_data(self, form, **kwargs):
        context_data = super(EditSessionView, self).get_context_data(
            form=form, **kwargs)
        if form.instance:
            context_data['lines'] = ImportLine.objects.filter(
                session=form.instance)
            if form.instance.imported:
                context_data['imported'] = form.instance.imported
        return context_data

    def form_valid(self, form):
        # Form input
        line_strings = form.cleaned_data['lines'].splitlines()
        regex = re.compile(form.cleaned_data['regex'])
        year = form.instance.year

        if form.instance.imported:
            context_data = super(EditSessionView, self).get_context_data(
                form=form)
            context_data['error'] = 'Denne rusliste er allerede importeret'
            return self.render_to_response(context_data)

        # Line objects
        lines = []
        position = 1
        studentnumbers = set()
        studentnumbers_duplicate = set()
        for line in line_strings:
            il = ImportLine(session=form.instance, line=line,
                            position=position, matched=False)
            position = position + 1

            m = regex.match(line)
            if m:
                il.matched = True
                il.rusclass = m.group('rusclass')
                il.name = m.group('name')
                il.studentnumber = m.group('studentnumber')
                if il.studentnumber in studentnumbers:
                    studentnumbers_duplicate.add(il.studentnumber)
                else:
                    studentnumbers.add(il.studentnumber)

            lines.append(il)

        lines_saved = False

        if studentnumbers_duplicate:
            context_data = super(EditSessionView, self).get_context_data(
                form=form)
            context_data['error'] = (
                'Årskortnummer/-numre er ikke unikke: %s' %
                ', '.join(studentnumbers_duplicate))
            return self.render_to_response(context_data)

        # Save form and perform bulk delete/insert of lines
        with transaction.atomic():
            importsession = form.save()
            ImportLine.objects.filter(session=form.instance).delete()
            ImportLine.objects.bulk_create(lines)
            lines_saved = True

        context_data = self.get_context_data(form=form)

        if lines_saved and 'create' in self.request.POST:
            class RusError(Exception):
                pass

            try:
                with transaction.atomic():

                    profiles = {}
                    studentnumbers = [il.studentnumber for il in lines]
                    qs = TutorProfile.objects.filter(
                        studentnumber__in=studentnumbers)
                    for tp in qs:
                        profiles[tp.studentnumber] = tp

                    rusclasses = {}

                    def get_rusclass(rusclass):
                        if rusclass in rusclasses:
                            return rusclasses[rusclass]
                        try:
                            o = RusClass.objects.get(
                                year=year, official_name=il.rusclass)
                        except RusClass.DoesNotExist:
                            o = RusClass.objects.create_from_official(
                                year=year, official_name=il.rusclass)
                            o.save()
                        rusclasses[rusclass] = o
                        return o

                    for il in lines:
                        if not il.matched:
                            continue

                        rusclass = get_rusclass(il.rusclass)

                        if il.studentnumber in profiles:
                            tp = profiles[il.studentnumber]
                            existing_rus = Rus.objects.filter(
                                profile=tp, year=year)
                            if existing_rus.exists():
                                raise RusError(
                                    ("Studienummer %s findes allerede i " +
                                     "ruslisterne") %
                                    (il.studentnumber,))
                        else:
                            tp = TutorProfile.objects.create(
                                name=il.name, studentnumber=il.studentnumber)
                            tp.get_or_create_user()
                            tp.set_default_email()

                        if form.cleaned_data['empty_initial_rusclass']:
                            initial_rusclass = None
                        else:
                            initial_rusclass = rusclass
                        Rus.objects.create(
                            profile=tp, year=year, rusclass=rusclass,
                            initial_rusclass=initial_rusclass)

                    importsession.imported = datetime.datetime.now()
                    importsession.save()
                    context_data['imported'] = importsession.imported

            except RusError as e:
                context_data['create_error'] = str(e)

        context_data['lines_saved'] = lines_saved

        return self.render_to_response(context_data)


# =============================================================================

class RusListView(TemplateView):
    template_name = 'reg/rus_list.html'

    def get_page_data(self):
        return {
            'rus_list': self.get_rus_list_data(),
            'rusclass_list': self.get_rusclass_list_data(),
            'note_list': self.get_note_list_data(),
            'change_list_newest': self.get_change_list_newest(),
        }

    def get_rusclass_list_data(self):
        return [{
            'handle': rusclass.handle,
            'internal_name': rusclass.internal_name,
            } for rusclass in self.get_rusclass_list()]

    def get_rus_list_data(self):
        return [rus.json_of() for rus in self.get_rus_list()]

    def get_context_data(self, **kwargs):
        context_data = super(RusListView, self).get_context_data(**kwargs)
        context_data['page_data_json'] = json.dumps(self.get_page_data())
        return context_data

    def get_change_list_newest(self):
        try:
            return ChangeLogEntry.objects.order_by('-pk')[:1].get().pk
        except ChangeLogEntry.DoesNotExist:
            return 0

    def get_note_list_data(self):
        rus_list = self.get_rus_list()
        rusclass_list = self.get_rusclass_list()

        rus_dict = {}
        for o in rus_list:
            rus_dict[o.pk] = o
        rusclass_dict = {}
        for o in rusclass_list:
            rusclass_dict[o.pk] = o

        rus_pks = frozenset(o.pk for o in rus_list)
        rusclass_pks = frozenset(o.pk for o in rusclass_list)

        rus_notes_qs = Note.objects.filter(
            subject_kind__exact='rus', subject_pk__in=rus_pks,
            deleted__isnull=True)
        rusclass_notes_qs = Note.objects.filter(
            subject_kind__exact='rusclass', subject_pk__in=rusclass_pks,
            deleted__isnull=True)

        note_list = list(rus_notes_qs) + list(rusclass_notes_qs)
        note_list_data = []

        for note in note_list:
            note_list_data.append({'pk': note.pk, 'note': note.json_of()})

        return note_list_data

    def get_rus_list(self):
        rus_list = Rus.objects.filter(year=self.request.year)
        return rus_list

    def get_rusclass_list(self):
        rusclass_list = RusClass.objects.filter(year=self.request.year)
        return rusclass_list


class RusCreateForm(forms.Form):
    name = forms.CharField(label='Navn')
    studentnumber = forms.CharField(label='Årskortnummer', required=False)
    email = forms.CharField(required=False, label='Email')
    rusclass = forms.ModelChoiceField(
        queryset=RusClass.objects.all(), label='Hold')
    arrived = forms.BooleanField(required=False, label='Ankommet')
    note = forms.CharField(required=False, label='Note')

    def __init__(self, **kwargs):
        self.year = kwargs.pop('year')
        super(RusCreateForm, self).__init__(**kwargs)
        f = self.fields['rusclass']
        f.queryset = f.queryset.filter(year=self.year)

    def clean_studentnumber(self):
        studentnumber = self.cleaned_data['studentnumber']
        existing = TutorProfile.objects.filter(studentnumber=studentnumber)
        existing = existing.filter(rus__year=self.year)
        if studentnumber:
            if existing.exists():
                raise forms.ValidationError(
                    "Årskortnummeret findes allerede på hjemmesiden.")
        else:
            studentnumber = None
        return studentnumber


class RusCreateView(FormView):
    template_name = 'reg/ruscreateform.html'
    form_class = RusCreateForm

    def get_form_kwargs(self):
        kwargs = super(RusCreateView, self).get_form_kwargs()
        kwargs['year'] = self.request.year
        return kwargs

    def get_context_data(self, **kwargs):
        context_data = super(RusCreateView, self).get_context_data(**kwargs)
        context_data['rusclass_list'] = self.get_rusclass_list()
        return context_data

    def get_rusclass_list(self):
        rusclass_list = RusClass.objects.filter(year=self.request.year)
        for rusclass in rusclass_list:
            rusclass.notes = Note.objects.filter(
                subject_kind='rusclass', subject_pk=rusclass.pk)
            arrived = Rus.objects.filter(rusclass=rusclass, arrived=True)
            rusclass.arrived_rus_count = arrived.count()
            rusclass.rus_count = Rus.objects.filter(rusclass=rusclass).count()
        return rusclass_list

    def get_initial(self):
        initial_data = super(RusCreateView, self).get_initial()
        initial_data['arrived'] = True
        return initial_data

    def form_valid(self, form):
        data = form.cleaned_data
        studentnumber = data['studentnumber']

        tutorprofile = None
        if studentnumber:
            existing = TutorProfile.objects.filter(studentnumber=studentnumber)
            if existing.exists():
                tutorprofile = existing.get()
                d1 = (data['name'], data['email'])
                d2 = (tutorprofile.name, tutorprofile.email)
                if d1 != d2:
                    # Redisplay form
                    data = copy.deepcopy(data)
                    data['name'] = tutorprofile.name
                    data['email'] = tutorprofile.email
                    # data['rusclass'] = data['rusclass'].pk
                    form = RusCreateForm(data=data, year=self.request.year)
                    form.add_error(
                        None,
                        'Årskortnummeret findes allerede. ' +
                        'Tryk "Opret" igen for at oprette russen. ' +
                        '%r' % (data['rusclass'],))
                    context_data = self.get_context_data(
                        form=form)
                    return self.render_to_response(context_data)

        with transaction.atomic():
            if tutorprofile is None:
                tutorprofile = TutorProfile.objects.create(
                    studentnumber=data['studentnumber'],
                    name=data['name'],
                    email=data['email'])
                if data['studentnumber'] is not None:
                    tutorprofile.get_or_create_user()
                tutorprofile.save()
            rus = Rus.objects.create(
                profile=tutorprofile,
                year=self.request.year,
                arrived=data['arrived'],
                rusclass=data['rusclass'])
            if data['note']:
                Note.objects.create(
                    subject_kind='rus',
                    subject_pk=rus.pk,
                    body=data['note'],
                    author=self.request.tutorprofile)
            return HttpResponseRedirect(reverse('reg_rus_list'))


class RPCError(Exception):
    pass


class RusListRPC(View):
    def get_data(self, request):
        try:
            pk = int(self.get_param('pk'))
        except ValueError:
            raise RPCError('Invalid pk')
        queryset = ChangeLogEntry.objects.filter(pk__gt=pk).order_by('pk')

        sleep_each = 1
        sleep_max = 5

        sleep_remaining = sleep_max

        while sleep_remaining > 0:
            # undo caching
            queryset = queryset.all()
            if not queryset:
                import time
                time.sleep(sleep_each)
                sleep_remaining -= sleep_each
                continue

            pk = max(entry.pk for entry in queryset)

            payloads = []

            for entry in queryset:
                payloads.append(entry.json_of())

            return {'pk': pk, 'payloads': payloads}

        return {'pk': pk, 'payloads': []}

    def get(self, request):
        try:
            data = self.get_data(request)
        except RPCError as e:
            data = {'error': str(e)}
        return HttpResponse(json.dumps(data))

    def get_param(self, param):
        try:
            return self.request.POST[param]
        except KeyError:
            try:
                return self.request.GET[param]
            except KeyError:
                raise RPCError('Missing parameter %s' % param)

    ACTIONS = (
        'arrived',
        'rusclass',
        'add_rus_note',
        'add_rusclass_note',
        'delete_note',
    )

    def log(self, **kwargs):
        kwargs['serialized_data'] = json.dumps(kwargs.pop('serialized_data'))
        return ChangeLogEntry.objects.create(
            author=self.author,
            **kwargs).json_of()

    def action_arrived(self, rus):
        rus.arrived = not rus.arrived
        rus.save()
        return self.log(
            kind='rus_arrived',
            related_pk=rus.pk,
            serialized_data=rus.json_of())

    def action_rusclass(self, rus, rusclass):
        rus.rusclass = rusclass
        rus.save()
        return self.log(
            kind='rus_rusclass',
            related_pk=rus.pk,
            serialized_data=rus.json_of())

    def action_add_rus_note(self, rus, body):
        note = Note.objects.create(
            subject_kind='rus',
            subject_pk=rus.pk,
            body=body,
            author=self.author)
        return self.log(
            kind='note_add',
            related_pk=note.pk,
            serialized_data=note.json_of())

    def action_add_rusclass_note(self, rusclass, body):
        note = Note.objects.create(
            subject_kind='rusclass',
            subject_pk=rusclass.pk,
            body=body,
            author=self.author)
        return self.log(
            kind='note_add',
            related_pk=note.pk,
            serialized_data=note.json_of())

    def action_delete_note(self, note):
        note.deleted = datetime.datetime.now()
        note.save()
        return self.log(
            kind='note_delete',
            related_pk=note.pk,
            serialized_data=note.json_of())

    def handle_post(self, request):
        self.author = request.tutorprofile

        action = self.get_param('action')
        if action not in self.ACTIONS:
            raise RPCError("Unknown action %u" % action)

        fn = getattr(self, 'action_'+action)

        import inspect
        args, varargs, keywords, defaults = inspect.getargspec(fn)
        params = {}

        if 'request' in args:
            params['request'] = request

        if 'rus' in args:
            try:
                params['rus'] = Rus.objects.get(
                    year=self.request.year,
                    profile__pk=self.get_param('rus'))
            except Rus.DoesNotExist:
                raise RPCError('No such rus')

        if 'rusclass' in args:
            try:
                params['rusclass'] = RusClass.objects.get(
                    year=self.request.year, handle=self.get_param('rusclass'))
            except Rus.DoesNotExist:
                raise RPCError('No such rusclass')

        if 'note' in args:
            try:
                params['note'] = Note.objects.get(pk=self.get_param('note'))
            except Note.DoesNotExist:
                raise RPCError('No such note')

        if 'body' in args:
            params['body'] = self.get_param('body')

        with transaction.atomic():
            return fn(**params)

    def post(self, request):
        try:
            data = self.handle_post(request)
        except RPCError as e:
            data = {'error': str(e)}
        return HttpResponse(json.dumps(data))


class RusChangesView(TemplateView):
    template_name = 'reg/rus_changes.html'

    def get_context_data(self, **kwargs):
        context_data = super(RusChangesView, self).get_context_data(**kwargs)
        context_data['rus_list'] = self.get_rus_list()
        return context_data

    def get_rus_list(self):
        from django.db.models import F
        rus_year = Rus.objects.filter(year=self.request.year)
        rus_list = (
            list(rus_year.exclude(rusclass=F('initial_rusclass'))) +
            list(rus_year.filter(initial_rusclass__isnull=True)))
        return rus_list


class RusChangesTableView(RusChangesView):
    template_name = 'reg/rus_changes.csv'


# =============================================================================

class HandoutListView(TemplateView):
    template_name = 'reg/handout_list.html'

    def get_context_data(self, **kwargs):
        context_data = super(HandoutListView, self).get_context_data(**kwargs)

        handouts = Handout.objects.filter(year=self.request.year)
        rusclasses = RusClass.objects.filter(year=self.request.year)

        responses = HandoutClassResponse.objects.filter(
            handout__in=handouts, rusclass__in=rusclasses)
        response_matrix = {}
        for response in responses:
            k = (response.handout.pk, response.rusclass.pk)
            response_matrix[k] = response

        for handout in handouts:
            handout.row = []
            for rusclass in rusclasses:
                x = (handout.pk, rusclass.pk)
                if x in response_matrix:
                    handout.row.append(response_matrix[x])
                else:
                    r = HandoutClassResponse(
                        handout=handout, rusclass=rusclass, color='red')
                    handout.row.append(r)

        context_data['handouts'] = handouts
        context_data['rusclasses'] = rusclasses

        return context_data


class HandoutForm(forms.ModelForm):
    kind = forms.ChoiceField(choices=Handout.KINDS)
    name = forms.CharField()
    note = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = Handout
        fields = ('kind', 'name', 'note')


class HandoutNewView(FormView):
    form_class = HandoutForm
    template_name = 'reg/handout_form.html'

    def get_context_data(self, **kwargs):
        context_data = super(HandoutNewView, self).get_context_data(**kwargs)

        presets = []
        existing = [(h.name, h.kind)
                    for h in Handout.objects.filter(year=self.request.year)]
        for i, (name, kind) in enumerate(Handout.PRESETS):
            if (name, kind) in existing:
                checked = ''
            else:
                checked = 'checked'
            p = {'i': i, 'name': name, 'kind': kind, 'checked': checked}
            presets.append(p)
        context_data['presets'] = presets

        return context_data

    def post(self, request):
        if request.POST.get('make_presets'):
            handouts = []
            for i, (name, kind) in enumerate(Handout.PRESETS):
                if request.POST.get('preset_%d' % i):
                    h = Handout(year=request.year, kind=kind, name=name)
                    handouts.append(h)
            for h in handouts:
                h.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(HandoutNewView, self).post(request)

    def form_valid(self, form):
        data = form.cleaned_data
        handout = Handout(
            year=self.request.year,
            kind=data['kind'], name=data['name'], note=data['note'])
        handout.save()
        return super(HandoutNewView, self).form_valid(form)

    def form_invalid(self, form):
        return super(HandoutNewView, self).form_invalid(form)

    def get_success_url(self):
        return reverse('handout_list')


class HandoutEditView(UpdateView):
    form_class = HandoutForm
    template_name = 'reg/handout_form.html'
    model = Handout

    def get_success_url(self):
        return reverse('handout_list')

    def get_context_data(self, **kwargs):
        context_data = super(HandoutEditView, self).get_context_data(**kwargs)
        context_data['delete'] = True
        return context_data

    def form_valid(self, form):
        if self.request.POST.get('delete'):
            form.instance.delete()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(HandoutEditView, self).form_valid(form)


class HandoutSummaryView(TemplateView):
    def get_template_names(self):
        kind = self.get_handout().kind
        if kind == 'subset':
            return ['reg/handout_summary.html']
        elif kind == 'note':
            return ['reg/handout_notes.html']
        else:
            raise AssertionError("Unknown handout kind")

    def get_handout(self):
        if not hasattr(self, '_handout'):
            self._handout = get_object_or_404(
                Handout, pk__exact=self.kwargs['handout'])
        return self._handout

    def get_classes(self):
        handout = self.get_handout()
        year = handout.year
        rusclasses = RusClass.objects.filter(year__exact=year)
        responses = {}
        for response in HandoutClassResponse.objects.filter(handout=handout):
            responses[response.rusclass.pk] = response

        qs = Rus.objects.filter(rusclass__in=rusclasses)
        qs = qs.select_related('rusclass', 'profile', 'profile__user')
        all_russes = list(qs.order_by('profile__studentnumber'))

        for rusclass in rusclasses:
            rusclass.russes = [
                rus for rus in all_russes if rus.rusclass.pk == rusclass.pk]
            rusclass.rus_total_count = len(rusclass.russes)
            if rusclass.pk in responses:
                rusclass.response = responses[rusclass.pk]
                rusclass.has_response = True
                qs = HandoutRusResponse.objects.filter(
                    handout=handout,
                    rus__in=rusclass.get_russes())
                response_queryset = qs.select_related(
                    'rus', 'rus__rusclass', 'rus__profile',
                    'rus__profile__user')
                rusclass.rus_checked_count = (
                    response_queryset.filter(checkmark=True).count())
                rus_responses = {}
                for r in response_queryset:
                    rus_responses[r.rus.pk] = r
                for rus in rusclass.russes:
                    if rus.pk in rus_responses:
                        rus.response = rus_responses[rus.pk]
            else:
                rusclass.has_response = False
                rusclass.rus_checked_count = 0

        return rusclasses

    def get_context_data(self, **kwargs):
        context_data = super(HandoutSummaryView, self).get_context_data(
            **kwargs)

        context_data['handout'] = self.get_handout()
        context_data['classes'] = self.get_classes()
        context_data['class_total_count'] = len(context_data['classes'])
        context_data['class_response_count'] = len(
            [c for c in context_data['classes'] if c.has_response])
        context_data['rus_checked_count'] = sum(
            r.rus_checked_count
            for r in context_data['classes'])
        context_data['rus_total_count'] = sum(
            r.rus_total_count
            for r in context_data['classes'])

        return context_data


class HandoutResponseForm(forms.Form):
    note = forms.CharField(required=False, widget=forms.Textarea)
    color = forms.ChoiceField(choices=HandoutClassResponse.COLORS,
                              label='Farve', widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        rus_list = kwargs.pop('rus_list')
        super(HandoutResponseForm, self).__init__(*args, **kwargs)

        for rus in rus_list:
            ck = forms.BooleanField(required=False)
            note = forms.CharField(required=False)
            self.fields['rus_%s_checkmark' % rus.pk] = ck
            self.fields['rus_%s_note' % rus.pk] = note


class HandoutResponseView(FormView):
    template_name = 'reg/handout_response.html'
    form_class = HandoutResponseForm

    def get_form_kwargs(self):
        kwargs = super(HandoutResponseView, self).get_form_kwargs()
        kwargs['rus_list'] = self.get_rus_list()
        return kwargs

    def get_initial(self):
        if self.handout_response.pk:
            color = self.handout_response.color
        else:
            color = 'green'
        data = {
            'note': self.handout_response.note,
            'color': color
        }
        for rus in self.rus_list:
            data['rus_%s_checkmark' % rus.pk] = rus.rus_response.checkmark
            data['rus_%s_note' % rus.pk] = rus.rus_response.note
        return data

    def dispatch(self, request, *args, **kwargs):
        try:
            handout = Handout.objects.get(
                year=request.year, pk=kwargs['handout'])
            rusclass = RusClass.objects.get(
                year=request.year, handle__exact=kwargs['rusclass'])
        except Handout.DoesNotExist:
            raise Http404()
        except RusClass.DoesNotExist:
            raise Http404()

        self.handout = handout
        self.rusclass = rusclass

        try:
            self.handout_response = HandoutClassResponse.objects.get(
                handout=handout, rusclass=rusclass)
        except HandoutClassResponse.DoesNotExist:
            self.handout_response = HandoutClassResponse(
                handout=handout, rusclass=rusclass)

        self.rus_list = self.get_rus_list()

        return super(HandoutResponseView, self).dispatch(
            request, *args, **kwargs)

    def get_rus_list(self):
        if self.handout.kind == 'note':
            return ()

        rus_list = self.rusclass.get_russes().order_by('profile__name')
        rus_list = rus_list.select_related('profile', 'profile__user')

        rus_responses = HandoutRusResponse.objects.filter(
            handout=self.handout, rus__in=rus_list)
        rus_responses = rus_responses.select_related('rus')

        rus_response_map = {}
        for rus_response in rus_responses:
            rus_response_map[rus_response.rus.pk] = rus_response

        for rus in rus_list:
            if rus.pk in rus_response_map:
                rus.rus_response = rus_response_map[rus.pk]
            else:
                rus.rus_response = HandoutRusResponse(
                    handout=self.handout, rus=rus)

        return rus_list

    def get_context_data(self, **kwargs):
        context_data = super(HandoutResponseView, self).get_context_data(
            **kwargs)

        context_data['handout'] = self.handout
        context_data['rusclass'] = self.rusclass
        context_data['handout_response'] = self.handout_response
        form = context_data['form']
        for rus in self.rus_list:
            rus.checkmark_field = form['rus_%s_checkmark' % rus.pk]
            rus.note_field = form['rus_%s_note' % rus.pk]
        context_data['rus_list'] = self.rus_list
        context_data['display_rus_list'] = self.handout.kind == 'subset'

        return context_data

    def form_valid(self, form):
        with transaction.atomic():
            data = form.cleaned_data
            self.handout_response.note = data['note']
            self.handout_response.color = data['color']
            self.handout_response.save()
            for rus in self.rus_list:
                rus.rus_response.checkmark = data['rus_%s_checkmark' % rus.pk]
                rus.rus_response.note = data['rus_%s_note' % rus.pk]
                rus.rus_response.save()

        return HttpResponseRedirect(reverse('handout_list'))

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(form=form, form_error=True))


class HandoutResponseDeleteView(TemplateView):
    template_name = 'reg/handout_response_delete.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            handout = Handout.objects.get(
                year=request.year, pk=kwargs['handout'])
            rusclass = RusClass.objects.get(
                year=request.year, handle__exact=kwargs['rusclass'])
        except Handout.DoesNotExist:
            raise Http404()
        except RusClass.DoesNotExist:
            raise Http404()

        self.handout = handout
        self.rusclass = rusclass

        try:
            self.handout_response = HandoutClassResponse.objects.get(
                handout=handout, rusclass=rusclass)
        except HandoutClassResponse.DoesNotExist:
            raise Http404()

        return super(HandoutResponseDeleteView, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(HandoutResponseDeleteView, self).get_context_data(
            **kwargs)

        context_data['handout'] = self.handout
        context_data['rusclass'] = self.rusclass
        context_data['handout_response'] = self.handout_response

        return context_data

    def post(self, request, *args, **kwargs):
        HandoutRusResponse.objects.filter(
            handout=self.handout, rus__rusclass=self.rusclass).delete()
        self.handout_response.delete()
        return HttpResponseRedirect(reverse('handout_list'))


class HandoutCrossReferenceForm(forms.Form):
    regex = forms.CharField(initial=r'(\S+)')
    studentnumbers = forms.CharField(widget=forms.Textarea)

    def clean_regex(self):
        regex = self.cleaned_data['regex']
        try:
            ro = re.compile(regex)
        except Exception as e:
            self.add_error('regex', str(e))
        return ro

    def clean(self):
        cleaned_data = super(HandoutCrossReferenceForm, self).clean()
        mo = cleaned_data['regex'].search(cleaned_data['studentnumbers'])
        if not mo:
            self.add_error('regex', 'Regex matcher intet i input')
        return cleaned_data


class HandoutCrossReference(FormView):
    form_class = HandoutCrossReferenceForm
    template_name = 'reg/handout_crossref.html'

    def get_object(self):
        h = Handout.objects.filter(pk=self.kwargs['pk'])
        h = h.prefetch_related(
            'handoutclassresponse_set',
            'handoutrusresponse_set',
            'handoutrusresponse_set__rus',
            'handoutrusresponse_set__rus__profile',
        )
        try:
            return h.get()
        except Handout.DoesNotExist:
            raise Http404()

    def form_valid(self, form):
        # Parse input text to find studentnumbers
        ro = form.cleaned_data['regex']
        text_input = form.cleaned_data['studentnumbers']
        mos = ro.finditer(text_input)
        studentnumbers = []
        match_dict = {}
        unknown = []

        i = 0
        skipped = []
        matches = 0

        for mo in mos:
            j = mo.start()
            skipped.append(text_input[i:j])
            i = mo.end()
            matches += 1

            sn = mo.group('studentnumber').strip()
            if sn:
                match_dict[sn] = mo.group(0)
                studentnumbers.append(sn)
            else:
                tp = None
                tried = []
                for k, v in mo.groupdict().items():
                    if k == 'studentnumber':
                        continue
                    if not v:
                        continue
                    try:
                        f = {k + '__iexact': v}
                        tp = TutorProfile.objects.get(**f)
                    except (TutorProfile.DoesNotExist, TutorProfile.MultipleObjectsReturned):
                        tried.append('%s=%s' % (k, v))
                        pass
                if tp:
                    sn = tp.studentnumber
                    match_dict[sn] = mo.group(0)
                    studentnumbers.append(sn)
                else:
                    unknown.append(
                        '%s (ikke fundet: %s)' % (mo.group(0), ', '.join(tried)))
        skipped.append(text_input[i:])
        skipped = [s for s in skipped if s.strip()]

        # Lookup studentnumbers in input
        tp_qs = TutorProfile.objects.filter(
            studentnumber__in=studentnumbers)
        tp_qs = tp_qs.prefetch_related('rus_set')
        year = self.request.year
        tp_dict = {tp.studentnumber: tp for tp in tp_qs}
        # Translate studentnumbers in input to Rus objects
        rus_dict = {}
        for sn, tp in tp_dict.items():
            try:
                rus = tp.rus_set.get(year=year)
            except Rus.DoesNotExist:
                rus = None
            rus_dict[sn] = {'rus': rus, 'line': match_dict[sn]}
        unknown_sns = sorted(set(studentnumbers) - set(rus_dict.keys()))
        # known = set(studentnumbers) & set(rus_dict.keys())
        unknown += [match_dict[sn] for sn in unknown_sns]

        handout = self.get_object()

        rr_qs = handout.handoutrusresponse_set.all()
        rr_dict = {rr.rus.profile.studentnumber: rr
                   for rr in rr_qs}

        # No HandoutRusResponse exists - assume unchecked
        missing_rr_sns = sorted(set(rus_dict.keys()) - set(rr_dict.keys()))
        for sn in missing_rr_sns:
            rr_dict[sn] = HandoutRusResponse(
                handout=handout, rus=rus_dict[sn]['rus'],
                note='Holdet er ikke fyldt ud')

        def sn_by_rusclass_name(sn):
            try:
                return (rus_dict[sn]['rus'].rusclass.internal_name,
                        rus_dict[sn]['rus'].profile.name)
            except KeyError:
                return ('', '')
        # Studentnumbers not in the input
        missing_input_sns = sorted(
            set(rr_dict.keys()) - set(studentnumbers),
            key=sn_by_rusclass_name)
        # Studentnumbers both in database and in input
        common_sns = sorted(set(studentnumbers) & set(rr_dict.keys()),
                            key=sn_by_rusclass_name)

        missing_checked = []
        missing_unchecked = []
        for sn in missing_input_sns:
            rr = rr_dict[sn]
            if rr.checkmark:
                missing_checked.append(rr)
            else:
                missing_unchecked.append(rr)

        common_checked = []
        common_unchecked = []
        by_rusclass = {}
        for sn in common_sns:
            rr = rr_dict[sn]
            if rr.checkmark:
                by_rusclass.setdefault(rr.rus.rusclass.handle, []).append(rr)
                common_checked.append(rr)
            else:
                common_unchecked.append(rr)
        by_rusclass = [
            {'rusclass': by_rusclass[k][0].rus.rusclass,
             'rus_list': by_rusclass[k]}
            for k in by_rusclass.keys()
        ]

        context_data = self.get_context_data(
            form=form, results=True, matches=matches,
            missing_checked=missing_checked,
            missing_unchecked=missing_unchecked,
            common_checked=common_checked,
            common_unchecked=common_unchecked,
            unknown=unknown, skipped=skipped,
            by_rusclass=by_rusclass)
        return self.render_to_response(context_data)


# =============================================================================

class RusInfoListView(ListView):
    template_name = 'reg/rusinfo_list.html'
    context_object_name = 'rusclasses'

    def get_queryset(self):
        qs = RusClass.objects.filter(year__exact=self.request.year)
        return qs.order_by('internal_name')

    def get(self, request):
        tutor = request.tutor
        if not tutor or not tutor.is_tutorbur():
            if tutor and tutor.rusclass:
                kwargs = {'handle': tutor.rusclass.handle}
                return HttpResponseRedirect(
                    reverse('rusinfo', kwargs=kwargs))
            else:
                return rusclass_required_error(request)
        return super(RusInfoListView, self).get(request)


class RusInfoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields')
        rus_list = kwargs.pop('rus_list')
        super(RusInfoForm, self).__init__(*args, **kwargs)
        self.rus_list = rus_list

        field_ctors = {
            'reset_password': forms.BooleanField,
            'email': forms.EmailField,
        }
        widget_ctors = {'reset_password': forms.CheckboxInput}
        sizes = {'street': 20, 'city': 15, 'email': 25, 'phone': 10}

        for rus in rus_list:
            for field in fields:
                field_ctor = field_ctors.get(field, forms.CharField)
                widget_ctor = widget_ctors.get(field, forms.TextInput)
                attrs = {}
                if field in sizes:
                    attrs['size'] = sizes[field]
                widget = widget_ctor(attrs=attrs)
                k = 'rus_%s_%s' % (rus.pk, field)
                self.fields[k] = field_ctor(required=False, widget=widget)

    def clean(self):
        cleaned_data = super(RusInfoForm, self).clean()
        for rus in self.rus_list:
            password_field = 'rus_%s_reset_password' % rus.pk
            email_field = 'rus_%s_email' % rus.pk
            phone_field = 'rus_%s_phone' % rus.pk
            if (cleaned_data[password_field]
                    and not cleaned_data[email_field]):
                msg = ('Du skal indtaste en emailadresse ' +
                       'for at nulstille kodeordet.')
                self.add_error(email_field, msg)

            try:
                phone = cleaned_data[phone_field]
                cleaned_data[phone_field] = TutorProfile.clean_phone(phone)
            except forms.ValidationError as e:
                self.add_error(phone_field, e)

        return cleaned_data


class RusInfoView(FormView):
    form_class = RusInfoForm
    template_name = 'reg/rusinfo_form.html'

    fields = ('street', 'city', 'email', 'phone', 'reset_password')

    def get_form_kwargs(self):
        kwargs = super(RusInfoView, self).get_form_kwargs()
        kwargs['fields'] = self.fields
        kwargs['rus_list'] = self.rus_list
        return kwargs

    def get_initial(self):
        data = {}

        for rus in self.rus_list:
            data['rus_%s_street' % rus.pk] = rus.profile.street
            data['rus_%s_city' % rus.pk] = rus.profile.city
            data['rus_%s_email' % rus.pk] = rus.profile.email
            data['rus_%s_phone' % rus.pk] = rus.profile.phone

        return data

    def dispatch(self, request, handle):
        if not request.tutor:
            return tutor_required_error(request)

        self.rusclass = get_object_or_404(
            RusClass, handle__exact=handle, year__exact=request.year)
        if not request.tutor.can_manage_rusclass(self.rusclass):
            return tutorbest_required_error(request)

        self.rus_list = self.get_rus_list()

        return super(RusInfoView, self).dispatch(request, handle=handle)

    def get_rus_list(self):
        return (self.rusclass.get_russes()
                .order_by('profile__name')
                .select_related('profile'))

    def get_context_data(self, **kwargs):
        context_data = super(RusInfoView, self).get_context_data(**kwargs)
        form = context_data['form']
        for rus in self.rus_list:
            for field in self.fields:
                k = 'rus_%s_%s' % (rus.pk, field)
                setattr(rus, '%s_field' % field, form[k])
                if form[k].errors:
                    rus.errors = 'errors'
        context_data['rus_list'] = self.rus_list
        context_data['rusclass'] = self.rusclass
        return context_data

    def form_valid(self, form):
        changes = 0
        messages = []
        with transaction.atomic():
            data = form.cleaned_data
            for rus in self.rus_list:
                in_street = data['rus_%s_street' % rus.pk]
                in_city = data['rus_%s_city' % rus.pk]
                in_email = data['rus_%s_email' % rus.pk]
                in_phone = data['rus_%s_phone' % rus.pk]
                in_password = data['rus_%s_reset_password' % rus.pk]
                in_profile = (in_street, in_city, in_email, in_phone)
                cur_profile = (rus.profile.street, rus.profile.city,
                               rus.profile.email, rus.profile.phone)

                if in_profile != cur_profile:
                    rus.profile.street = in_street
                    rus.profile.city = in_city
                    rus.profile.email = in_email
                    rus.profile.phone = in_phone
                    rus.profile.save()
                    changes += 1

                if in_password:
                    if not rus.profile.studentnumber:
                        e = forms.ValidationError(
                            'Rus har intet årskortnummer')
                        form.add_error('rus_%s_reset_password' % rus.pk, e)
                        continue
                    pwlength = 8
                    try:
                        p = subprocess.Popen(
                            ['/usr/bin/pwgen', '--capitalize', '--numerals',
                             str(pwlength), '1'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
                        pw, err = p.communicate()
                        pw = pw.strip()
                    except:
                        letters = string.ascii_letters + string.digits
                        pw = 'r'+''.join(
                            random.choice(letters) for i in range(pwlength))
                    rus.profile.user.set_password(pw)

                    msg = make_password_reset_message(
                        rus.profile, self.request.tutorprofile, pw)
                    messages.append(msg)

                    rus.profile.user.save()
                    changes += 1

        send_messages(messages)

        # Redisplay form
        kwargs = self.get_form_kwargs()
        kwargs.pop('data', None)
        kwargs.pop('files', None)
        form = RusInfoForm(**kwargs)
        return self.render_to_response(
            self.get_context_data(form=form, form_saved=True, changes=changes,
                                  emails=len(messages)))

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(form=form, form_errors=True))


class RusInfoDumpView(TemplateView):
    template_name = 'contacts.csv'

    def dispatch(self, request, handle):
        if not request.tutor:
            return tutor_required_error(request)

        self.rusclass = get_object_or_404(
            RusClass, handle__exact=handle, year__exact=request.year)
        if not request.tutor.can_manage_rusclass(self.rusclass):
            return tutorbest_required_error(request)

        self.person_list = self.get_person_list()

        return super(RusInfoDumpView, self).dispatch(request)

    def get_person_list(self):
        rus_list = self.rusclass.get_russes()
        tutor_list = self.rusclass.get_tutors()
        person_list = TutorProfile.objects.filter(
            Q(rus__in=rus_list) |
            Q(tutor__in=tutor_list)).distinct()
        person_list = person_list.order_by('studentnumber')
        return person_list

    def get_context_data(self, **kwargs):
        context_data = super(RusInfoDumpView, self).get_context_data(**kwargs)
        context_data['person_list'] = self.person_list
        return context_data

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = 'text/csv'
        return super(RusInfoDumpView, self).render_to_response(
            context, **response_kwargs)


# =============================================================================

def get_lightbox_state_by_study(year):
    states = LightboxRusClassState.objects.get_for_year(year)
    if not states:
        states = LightboxRusClassState.objects.get_for_year(year - 1)
        for s in states:
            s.color = random.choice(s.COLORS)[0]

    study_dict = {}
    for state in states:
        rusclass = state.rusclass
        study = rusclass.get_study()
        l = study_dict.setdefault(study, [])
        l.append(state)

    study_list = []
    for study in sorted(study_dict.keys()):
        l = study_dict[study]
        o = {'study': study}
        o['rusclasses'] = sorted(l, key=lambda state: state.rusclass.handle)
        study_list.append(o)

    return study_list


def get_lightbox_state(year):
    note = LightboxNote.objects.get_for_year(year)
    by_study = get_lightbox_state_by_study(year)
    return {'note': note, 'by_study': by_study}


class LightboxView(TemplateView):
    template_name = 'reg/burtavle.html'

    def get_context_data(self, **kwargs):
        context_data = super(LightboxView, self).get_context_data(**kwargs)

        d = get_lightbox_state(self.request.year)
        context_data['note'] = d['note']
        context_data['state_by_study'] = d['by_study']

        return context_data


burtavle = LightboxView.as_view()


class BurtavleFramesetView(TemplateView):
    template_name = 'reg/burtavle_frameset.html'


burtavle_frameset = BurtavleFramesetView.as_view()


class LightboxAdminViewResponse(Exception):
    def __init__(self, o):
        self.response = o


class LightboxAdminForm(forms.Form):
    COLORS = (
        ('green', 'Grøn'),
        ('yellow', 'Gul'),
        ('red', 'Rød'),
    )

    rusclass = forms.CharField(required=False)
    color = forms.ChoiceField(choices=COLORS, widget=forms.RadioSelect)
    note = forms.CharField(required=False, widget=forms.Textarea())


class LightboxAdminView(LightboxView):
    template_name = 'reg/burtavle_admin.html'

    def get_form(self):
        note = LightboxNote.objects.get_for_year(self.request.year)
        form = LightboxAdminForm({'note': note.note, 'color': note.color})
        return form

    def get_post_response(self, request):
        form = LightboxAdminForm(request.POST)
        if not form.is_valid():
            return {'error': form.errors}

        data = form.cleaned_data
        if data['rusclass']:
            try:
                rusclass = RusClass.objects.get(
                    year=request.year, handle=data['rusclass'])
            except RusClass.DoesNotExist:
                return {'error': 'no such rusclass'}

            try:
                state = LightboxRusClassState.objects.get(rusclass=rusclass)
            except LightboxRusClassState.DoesNotExist:
                state = LightboxRusClassState(rusclass=rusclass)
        else:
            state = LightboxNote.objects.get_for_year(request.year)

        state.color = data['color']
        state.note = data['note']
        state.author = request.tutorprofile
        state.save()
        return {'success': True}

    def post(self, request):
        try:
            data = self.get_post_response(request)
        except LightboxAdminViewResponse as e:
            data = e.response
        return HttpResponse(json.dumps(data))

    def get_context_data(self, **kwargs):
        context_data = super(LightboxAdminView, self).get_context_data(
            **kwargs)
        context_data['form'] = self.get_form()
        return context_data


class ArrivedStatsView(TemplateView):
    template_name = 'reg/arrived_stats.html'

    @staticmethod
    def kot_optag():
        return {
            year: dict(zip('mat mok nano it fys dat'.split(), numbers))
            for year, numbers in [
                (2007, [67, 29, 41, '-', 80, 73]),
                (2008, [65, 28, 39, 50, 67, 114]),
                (2009, [54, 26, 35, 52, 75, 108]),
                (2010, [77, 37, 34, 53, 106, 114]),
                (2011, [75, 61, 45, 70, 109, 155]),
                (2012, [100, 83, 47, 69, 114, 154]),
                (2013, [113, 74, 74, 70, 116, 155]),
                (2014, [72, 81, 56, 65, 103, 170]),
                (2015, [72, 86, 54, 68, 116, 185]),
                (2016, [77, 67, 52, 52, 110, 130]),
            ]
        }

    @staticmethod
    def get_year_list():
        kot = ArrivedStatsView.kot_optag()
        old_study = 'dat fys mat mok nano it'.split()
        old_data = dict(
            [(2012, dict(zip(old_study,
                             [(142, 153), (114, 115), (65, 71),
                              (117, 124), (93, 96), (48, 50)]))),
             (2011, dict(zip(old_study,
                             [(154, 161), (105, 109), (59, 62),
                              (87, 90), (69, 71), (45, 46)]))),
             (2010, dict(zip(old_study,
                             [(115, 119), (109, 111), (59, 60),
                              (78, 84), (44, 46), (37, 37)]))),
             (2009, dict(zip(old_study,
                             [(107, 119), (78, 84), (63, 67),
                              (70, 78), (22, 26), (35, 36)]))),
             (2008, dict(zip(old_study,
                             [('-', 119), ('-', 73), ('-', 51),
                              ('-', 63), ('-', 28), ('-', 43)]))),
             (2007, dict(zip(old_study,
                             [('-', '-'), ('-', '-'), ('-', '-'),
                              ('-', '-'), ('-', '-'), ('-', '-')]))),
            ]
        )
        years = sorted(
            set(Rus.objects.values_list('year', flat=True).distinct()) |
            set(kot.keys()) |
            set(old_data.keys()))
        rows = []
        for year in years:
            cells = []
            kot_year = kot.get(year, {})
            for official_name, handle, internal_name in settings.RUSCLASS_BASE:
                kot_study = kot_year.get(handle, '-')

                o = old_data.get(year, {}).get(handle, None)
                if o:
                    arrived, count = o
                else:
                    qs = Rus.objects.filter(
                        year=year, rusclass__handle__startswith=handle)
                    count = qs.count()
                    arrived = qs.filter(arrived=True).count()

                cells.append({
                    'handle': handle,
                    'name': internal_name,
                    'kot': kot_study,
                    'count': count,
                    'arrived': arrived,
                })
            rows.append({
                'year': year,
                'cells': cells,
            })
        return rows

    def get_context_data(self, **kwargs):
        context_data = super(ArrivedStatsView, self).get_context_data(**kwargs)
        context_data['year_list'] = self.get_year_list()
        return context_data


class StudentnumberListView(ListView):
    template_name = 'reg/studentnumber_list.html'
    model = Rus

    def get_queryset(self):
        return Rus.objects.filter(
            year=self.request.year,
            profile__studentnumber__isnull=True)


class StudentnumberForm(forms.Form):
    studentnumber = forms.CharField(label='Årskortnummer')


class StudentnumberView(FormView):
    template_name = 'reg/studentnumber_set.html'
    form_class = StudentnumberForm

    def get_rus(self):
        return get_object_or_404(
            Rus,
            profile__pk=self.kwargs['pk'],
            year=self.request.year)

    def get_initial(self):
        initial = super(StudentnumberView, self).get_initial()
        initial['studentnumber'] = self.get_rus().profile.studentnumber or ''
        return initial

    def get_context_data(self, **kwargs):
        context_data = super(StudentnumberView, self).get_context_data(
            **kwargs)
        context_data['rus'] = self.get_rus()
        return context_data

    def form_valid(self, form):
        sn = form.cleaned_data['studentnumber']
        existing = Rus.objects.filter(profile__studentnumber=sn)
        if existing.exists():
            e = forms.ValidationError(
                'Årskortnummeret findes allerede')
            form.add_error('studentnumber', e)
            return self.render_to_response(
                self.get_context_data(form=form))
        rus = self.get_rus()
        rus.profile.studentnumber = sn
        rus.profile.save()
        rus.profile.get_or_create_user()
        return HttpResponseRedirect(reverse('studentnumber_list'))
