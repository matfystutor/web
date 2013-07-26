# vim: set fileencoding=utf8:
import re
import exceptions
import datetime

from django.utils import dateformat
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.shortcuts import get_object_or_404, render, redirect, render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.views.decorators.http import condition
from django.views.generic import ListView, FormView, UpdateView, TemplateView, View, CreateView
from django.views.generic.edit import ProcessFormView
from django.contrib.auth.models import User

from .. import settings
from ..settings import YEAR
from ..tutor.models import RusClass, TutorProfile, Rus
from ..tutor.auth import user_tutor_data, tutor_required_error, NotTutor

from .models import ImportSession, ImportLine, Note, ChangeLogEntry, ChangeLogEffect, Handout, HandoutRusResponse, HandoutClassResponse

class ChooseSessionView(ListView):
    model = ImportSession

    def get_queryset(self):
        return ImportSession.objects.filter(year__exact=YEAR)

class NewSessionView(ProcessFormView):
    def post(self, request):
        importsession = ImportSession(year=YEAR, author=request.user.get_profile())
        importsession.save()
        return HttpResponseRedirect(reverse('import_session_edit', kwargs={'pk': importsession.pk}))

class EditSessionForm(forms.ModelForm):
    year = forms.CharField(required=False)
    author = forms.CharField(required=False)
    imported = forms.CharField(required=False)

    regex = forms.CharField()
    name = forms.CharField()
    lines = forms.CharField(widget=forms.Textarea)

    def clean_regex(self):
        data = self.cleaned_data['regex']
        try:
            r = re.compile(data)
        except re.error, v:
            raise forms.ValidationError(u"Fejl i regulært udtryk: "+unicode(v))

        return data

    def clean_year(self):
        return self.instance.year

    def clean_author(self):
        return self.instance.author

    def clean_imported(self):
        return self.instance.imported

    def clean(self):
        cleaned_data = super(EditSessionForm, self).clean()

        regex = cleaned_data.get('regex')
        lines = cleaned_data.get('lines')

        # Named groups we expect in the input
        expected = frozenset(('rusclass', 'name', 'studentnumber'))
        expected_string = u', '.join('(?P<'+k+'>...)' for k in expected) + u'.'

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
                        raise forms.ValidationError(u"Det regulære udtryk matcher UNAVNGIVNE grupper. "
                                +u"Brug kun navngivne grupper "+expected_string)
                    groupkeys = frozenset(groupdict.keys())
                    if not groupkeys.issubset(expected):
                        raise forms.ValidationError(u"Det regulære udtryk matcher UKENDTE gruppenavne. "
                                +u"Brug kun navngivne grupper "+expected_string)
                    if not expected.issubset(groupkeys):
                        raise forms.ValidationError(u"Det regulære udtryk matcher IKKE "
                                +u"alle de navngivne grupper "+expected_string)

                    for n, v in groupdict.items():
                        if v == '':
                            raise forms.ValidationError(u"Det regulære udtryk matcher gruppen '"
                                    +n+u"' som den tomme streng.")

            if matches == 0:
                raise forms.ValidationError(u"Det regulære udtryk matcher ingen strenge i input.")

        return cleaned_data

    class Meta:
        model = ImportSession

class EditSessionView(UpdateView):
    form_class = EditSessionForm
    template_name = 'reg/edit_session_form.html'

    def get_form(self, form_class):
        form = super(EditSessionView, self).get_form(form_class)
        if form.instance and form.instance.pk is not None:
            lines = u'\n'.join(il.line
                    for il in ImportLine.objects.filter(session=form.instance).order_by('position'))
            form.fields['lines'].initial = lines
        return form

    def get_object(self):
        return ImportSession.objects.get(pk=self.kwargs.get('pk'))

    def get_context_data(self, form, **kwargs):
        context_data = super(EditSessionView, self).get_context_data(form=form, **kwargs)
        if form.instance:
            context_data['lines'] = ImportLine.objects.filter(session=form.instance)
            if form.instance.imported:
                context_data['imported'] = form.instance.imported
        return context_data

    def form_valid(self, form):
        # Form input
        line_strings = form.cleaned_data['lines'].splitlines()
        regex = re.compile(form.cleaned_data['regex'])
        year = form.instance.year

        if form.instance.imported:
            context_data = super(EditSessionView, self).get_context_data(form=form)
            context_data['error'] = u'Denne rusliste er allerede importeret'
            return self.render_to_response(context_data)

        # Line objects
        lines = []
        position = 1
        for line in line_strings:
            il = ImportLine(session=form.instance, line=line, position=position, matched=False)
            position = position + 1

            m = regex.match(line)
            if m:
                il.matched = True
                il.rusclass = m.group('rusclass')
                il.name = m.group('name')
                il.studentnumber = m.group('studentnumber')

            lines.append(il)

        lines_saved = False

        # Save form and perform bulk delete/insert of lines
        from django.db import transaction
        with transaction.commit_on_success():
            importsession = form.save()
            ImportLine.objects.filter(session=form.instance).delete()
            ImportLine.objects.bulk_create(lines)
            lines_saved = True

        context_data = self.get_context_data(form=form)

        if lines_saved and 'create' in self.request.POST:
            class RusError(exceptions.Exception):
                pass

            try:
                with transaction.commit_on_success():

                    profiles = {}
                    for tp in TutorProfile.objects.filter(studentnumber__in=(il.studentnumber for il in lines)):
                        profiles[tp.studentnumber] = tp

                    rusclasses = {}
                    def get_rusclass(rusclass):
                        if rusclass in rusclasses:
                            return rusclasses[rusclass]
                        try:
                            o = RusClass.objects.get(year=year, official_name=il.rusclass)
                        except RusClass.DoesNotExist:
                            o = RusClass.objects.create_from_official(year=year, official_name=il.rusclass)
                            o.save()
                        rusclasses[rusclass] = o
                        return o

                    for il in lines:
                        if not il.matched:
                            continue

                        rusclass = get_rusclass(il.rusclass)

                        if il.studentnumber in profiles:
                            tp = profiles[il.studentnumber]
                            # TODO: check if name is correct; otherwise log the change
                        else:
                            first_name, last_name = il.name.split(None, 1)
                            u = User.objects.create(username=il.studentnumber, first_name=first_name, last_name=last_name)
                            tp = TutorProfile.objects.create(studentnumber=il.studentnumber, user=u)

                        rus = Rus.objects.create(profile=tp, year=year, rusclass=rusclass)

                    importsession.imported = datetime.datetime.now()
                    print importsession.imported
                    importsession.save()
                    context_data['imported'] = importsession.imported

            except RusError, e:
                context_data['create_error'] = unicode(e)

        context_data['lines_saved'] = lines_saved

        return self.render_to_response(context_data)

class ChangeClassForm(forms.Form):
    rus = forms.ModelChoiceField(queryset=Rus.objects.filter(year__exact=YEAR))
    rusclass = forms.ModelChoiceField(queryset=RusClass.objects.filter(year__exact=YEAR), required=False)

class ChangeClassView(FormView):
    form_class = ChangeClassForm

    def get(self, request):
        return self.http_method_not_allowed(request)

    def form_invalid(self):
        return HttpResponseBadRequest()

    def save_change(self, form):
        d = user_tutor_data(self.request.user)
        data = form.clean()
        rus = data['rus']
        rusclass = data['rusclass']
        oldrusclass_pk = rus.rusclass.pk if rus.rusclass else ""
        rusclass_pk = rusclass.pk if rusclass else ""
        rusclass_name = rusclass.internal_name if rusclass else 'Intet hold'

        from django.db import transaction
        with transaction.commit_on_success():
            short_message = (rus.profile.studentnumber
                    +u' skifter hold til '+rusclass_name
                    +u' - '+d.profile.get_full_name())
            logentry = ChangeLogEntry(
                    author=d.profile,
                    short_message=short_message,
                    message=short_message,
                    can_rollback=True)
            logentry.save()
            logeffect = ChangeLogEffect(
                    entry=logentry,
                    model='rus',
                    pk=rus.pk,
                    what='modified',
                    field='rusclass',
                    old_value=oldrusclass_pk,
                    new_value=rusclass_pk)
            logeffect.save()
            rus.rusclass = rusclass
            rus.save()
            return logentry

    def form_valid(self, form):
        self.save_change(form)
        return HttpResponseRedirect(reverse('reg_rus_list'))

class AjaxChangeClassView(ChangeClassView):
    def form_valid(self, form):
        logentry = self.save_change(form)
        response = {'undo_link': reverse('reg_undo', kwargs={'pk': logentry.pk})}
        import json
        return HttpResponse(json.dumps(response), content_type='application/json')

class ChangeArrivedView(View):
    def save_change(self, request, ruspk):
        d = user_tutor_data(request.user)
        author = d.profile

        rus = get_object_or_404(Rus, pk=ruspk, year=YEAR)

        from django.db import transaction
        with transaction.commit_on_success():
            old_value = rus.arrived
            new_value = not rus.arrived

            negation_string = u'ikke ' if not new_value else u''
            short_message = (rus.profile.studentnumber
                    +u' '+rus.profile.get_full_name()+u' er '+negation_string+'ankommet '+rus.rusclass.internal_name
                    +u' - '+author.get_full_name())
            logentry = ChangeLogEntry(
                    author=author,
                    short_message=short_message,
                    message=short_message,
                    can_rollback=True)
            logentry.save()
            logeffect = ChangeLogEffect(
                    entry=logentry,
                    model='rus',
                    pk=rus.pk,
                    what='modified',
                    field='arrived',
                    old_value="1" if old_value else "",
                    new_value="1" if new_value else "")
            logeffect.save()
            rus.arrived = new_value
            rus.save()
            return logentry

    def post(self, request, pk):
        self.save_change(request=request, ruspk=pk)
        return HttpResponseRedirect(reverse('reg_rus_list'))


class AjaxChangeArrivedView(ChangeArrivedView):
    def post(self, request, pk):
        logentry = self.save_change(request=request, ruspk=pk)
        response = {'undo_link': reverse('reg_undo', kwargs={'pk': logentry.pk})}
        import json
        return HttpResponse(json.dumps(response), content_type='application/json')

class UndoError(Exception):
    def __init__(self, response):
        self.response = response

class UndoView(View):
    def perform_undo(self, request, pk):
        d = user_tutor_data(request.user)
        logentry = get_object_or_404(ChangeLogEntry, pk=pk, can_rollback__exact=True, deleted__isnull=True)

        undo_message = u'Fortrød ændring "'+logentry.short_message+u'" - '+d.profile.get_full_name()
        undo_logentry = ChangeLogEntry(
                author=d.profile,
                hidden=datetime.datetime.now(),
                short_message=undo_message,
                message=undo_message,
                can_rollback=False)
        undo_logentry.save()

        effects = ChangeLogEffect.objects.filter(entry=logentry)
        for effect in effects:
            if effect.model == u'rus':
                field = effect.field
                rus = Rus.objects.get(pk=effect.pk)
                if field == u'arrived':
                    cur_value = rus.arrived
                    old_value = bool(effect.old_value)
                    new_value = bool(effect.new_value)
                elif field == u'rusclass':
                    cur_value = rus.rusclass.pk
                    old_value = int(effect.old_value)
                    new_value = int(effect.new_value)
                else:
                    raise UndoError({'error': u'unknown rus field '+field})
                if cur_value != new_value:
                    raise UndoError({'error':
                        (u'bad current value for rus {0} field {1} (was {2}, expected {3})'
                            .format(rus, field, cur_value, effect.new_value))})
                if field == u'arrived':
                    rus.arrived = old_value
                elif field == u'rusclass':
                    rus.rusclass = RusClass.objects.get(pk=old_value)
                rus.save()
                undo_logeffect = ChangeLogEffect(
                        entry=undo_logentry,
                        model=effect.model,
                        pk=effect.pk,
                        field=effect.field,
                        what=u'modified',
                        old_value=effect.new_value,
                        new_value=effect.old_value)
                undo_logeffect.save()
            else:
                raise UndoError({'error':
                    u'Unknown model {0}'.format(effect.model)})
        logentry.hidden = datetime.datetime.now()
        logentry.save()
        return {'success': True}

    def post(self, request, pk):
        try:
            from django.db import transaction
            with transaction.commit_on_success():
                self.perform_undo(request, pk)
            return HttpResponseRedirect(reverse('reg_rus_list'))
        except UndoError as e:
            response = e.response
        import json
        return HttpResponse(json.dumps(response), content_type='application/json')

# This should probably be fixed some day.
class CachedQuerySetHack(object):
    def __init__(self, queryset):
        self._queryset = queryset

    # Default queryset all() "forgets" the cached result
    # and produces a deep copy of the object.
    # This might be a feature to some, but in our case we want the results to be cached.
    def all(self):
        return self

    def __iter__(self):
        return iter(self._queryset)

class RusListView(TemplateView):
    template_name = 'reg/rus_list.html'

    def get_change_class_form_rusclass(self):
        ccf = ChangeClassForm()
        # This field is displayed multiple times on the page. Don't hit the DB every time!
        ccf.fields['rusclass'].queryset = CachedQuerySetHack(RusClass.objects.filter(year=YEAR))
        return ccf['rusclass']

    def get_context_data(self, **kwargs):
        context_data = super(RusListView, self).get_context_data(**kwargs)
        context_data['rus_list'] = self.get_rus_list()
        context_data['change_class_form_rusclass'] = self.get_change_class_form_rusclass()
        context_data['change_list'] = ChangeLogEntry.objects.filter(deleted__isnull=True, hidden__isnull=True).order_by('-time')

        try:
            change_list_newest = ChangeLogEntry.objects.order_by('-pk')[:1].get().pk
        except ChangeLogEntry.DoesNotExist:
            change_list_newest = 0
        context_data['change_list_newest'] = change_list_newest

        return context_data

    def get_rus_list(self):
        rus_list = Rus.objects.filter(year=YEAR).select_related('rusclass', 'profile', 'profile__user', 'profile__activation').order_by('rusclass', 'profile__studentnumber')

        rus_pks = frozenset(rus.pk for rus in rus_list)
        rusclass_pks = frozenset(rus.rusclass.pk for rus in rus_list if rus.rusclass is not None)

        rus_notes_qs = Note.objects.filter(subject_kind__exact='rus', subject_pk__in=rus_pks,
                deleted__isnull=True,
                superseded__isnull=True)
        rusclass_notes_qs = Note.objects.filter(subject_kind__exact='rusclass', subject_pk__in=rusclass_pks,
                deleted__isnull=True,
                superseded__isnull=True)
        rus_notes = {}
        rusclass_notes = {}
        for note in rus_notes_qs:
            rus_notes.setdefault(note.subject_pk, []).append(note)
        for note in rusclass_notes_qs:
            rusclass_notes.setdefault(note.subject_pk, []).append(note)

        for rus in rus_list:
            rus.notes = rus_notes.get(rus.pk, ())
            if rus.rusclass is not None:
                rus.rusclass.notes = rusclass_notes.get(rus.rusclass.pk, ())

        return rus_list

class NotesForm(forms.Form):
    subject_kind = forms.ChoiceField(choices=((a,a) for a in ('rus', 'rusclass', 'tutor')))
    subject_pk = forms.IntegerField()
    body = forms.CharField(required=False)

    new_note = forms.BooleanField()



class NotesView(FormView):
    form_class = NotesForm

    def get(self, request):
        return self.http_method_not_allowed(request)

    def form_invalid(self):
        return HttpResponseBadRequest()

    def form_valid(self, form):
        d = user_tutor_data(self.request.user)
        data = form.clean()
        if 'new_note' in data:
            Note(subject_kind=data['subject_kind'],
                    subject_pk=data['subject_pk'],
                    body=data['body'],
                    author=d.profile).save()
        return HttpResponseRedirect(reverse('reg_rus_list'))

class RPCForm(forms.Form):
    pk = forms.IntegerField()

class RusListRPC(View):
    def get_data(self, request):
        form = RPCForm(request.GET)
        if not form.is_valid():
            return {'errors': form.errors}
        pk = form.cleaned_data['pk']
        queryset = ChangeLogEntry.objects.filter(pk__gt=pk)

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
                payloads.append({
                    'method': 'change_log_entry',
                    'data': {
                        'time': dateformat.format(entry.time, "d M y, H:i"),
                        'short_message': unicode(entry.short_message),
                        'can_rollback': entry.can_rollback,
                    }
                })
                for effect in entry.changelogeffect_set.all():
                    payloads.append({
                        'method': 'change_log_effect',
                        'data': {
                            'model': effect.model,
                            'pk': effect.pk,
                            'what': effect.what,
                            'field': effect.field,
                            'old_value': effect.old_value,
                            'new_value': effect.new_value,
                        }
                    })

            return {'pk': pk,
                    'payloads': payloads}

        return {'pk': pk, 'payloads': []}

    def get(self, request):
        import json

        data = self.get_data(request)
        return HttpResponse(json.dumps(data))


class HandoutListView(TemplateView):
    template_name = 'reg/handout_list.html'

    def get_context_data(self, **kwargs):
        context_data = super(HandoutListView, self).get_context_data(**kwargs)

        handouts = Handout.objects.filter(year=YEAR)
        rusclasses = RusClass.objects.filter(year=YEAR)

        responses = HandoutClassResponse.objects.filter(handout__in=handouts, rusclass__in=rusclasses)
        response_matrix = {}
        for response in responses:
            response_matrix[(response.handout.pk, response.rusclass.pk)] = response

        for handout in handouts:
            handout.row = []
            for rusclass in rusclasses:
                x = (handout.pk, rusclass.pk)
                if x in response_matrix:
                    handout.row.append(response_matrix[x])
                else:
                    handout.row.append(HandoutClassResponse(handout=handout, rusclass=rusclass))

        context_data['handouts'] = handouts
        context_data['rusclasses'] = rusclasses

        return context_data

class HandoutForm(forms.Form):
    kind = forms.ChoiceField(choices=Handout.KINDS)
    name = forms.CharField()
    note = forms.CharField(required=False, widget=forms.Textarea)

class HandoutNewView(FormView):
    form_class = HandoutForm
    template_name = 'reg/handout_form.html'

    def get_context_data(self, **kwargs):
        context_data = super(HandoutNewView, self).get_context_data(**kwargs)

        context_data['presets'] = [{'name': name, 'kind': kind} for name, kind in Handout.PRESETS]

        return context_data

    def form_valid(self, form):
        data = form.cleaned_data
        handout = Handout(year=YEAR,
                kind=data['kind'], name=data['name'], note=data['note'])
        handout.save()
        return super(HandoutNewView, self).form_valid(form)

    def form_invalid(self, form):
        return super(HandoutNewView, self).form_invalid(form)

    def get_success_url(self):
        return reverse('handout_list')

class HandoutResponseForm(forms.Form):
    note = forms.CharField(required=False, widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        rus_list = kwargs.pop('rus_list')
        super(HandoutResponseForm, self).__init__(*args, **kwargs)

        for rus in rus_list:
            self.fields['rus_%s_checkmark' % rus.pk] = forms.BooleanField(required=False)
            self.fields['rus_%s_note' % rus.pk] = forms.CharField(required=False)

class HandoutResponseView(FormView):
    template_name = 'reg/handout_response.html'
    form_class = HandoutResponseForm

    def get_form_kwargs(self):
        kwargs = super(HandoutResponseView, self).get_form_kwargs()
        kwargs['rus_list'] = self.get_rus_list()
        return kwargs

    def get_initial(self):
        data = {'note': self.handout_response.note}
        for rus in self.rus_list:
            data['rus_%s_checkmark' % rus.pk] = rus.rus_response.checkmark
            data['rus_%s_note' % rus.pk] = rus.rus_response.note
        return data

    def dispatch(self, request, *args, **kwargs):
        try:
            handout = Handout.objects.get(
                    year=YEAR, pk=kwargs['handout'])
            rusclass = RusClass.objects.get(
                    year=YEAR, handle__exact=kwargs['rusclass'])
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

        return super(HandoutResponseView, self).dispatch(request, *args, **kwargs)

    def get_rus_list(self):
        if self.handout.kind == 'note':
            return ()

        rus_list = (
                Rus.objects.filter(rusclass=self.rusclass)
                .order_by('profile__studentnumber')
                .select_related('profile', 'profile__user'))
        rus_responses = (
                HandoutRusResponse.objects.filter(handout=self.handout, rus__in=rus_list)
                .select_related('rus'))
        rus_response_map = {}

        for rus_response in rus_responses:
            rus_response_map[rus_response.rus.pk] = rus_response

        for rus in rus_list:
            if rus.pk in rus_response_map:
                rus.rus_response = rus_response_map[rus.pk]
            else:
                rus.rus_response = HandoutRusResponse(handout=self.handout, rus=rus)

        return rus_list

    def get_context_data(self, **kwargs):
        context_data = super(HandoutResponseView, self).get_context_data(**kwargs)

        context_data['handout'] = self.handout
        context_data['rusclass'] = self.rusclass
        context_data['handout_response'] = self.handout_response
        form = context_data['form']
        for rus in self.rus_list:
            rus.checkmark_field = form['rus_%s_checkmark' % rus.pk]
            rus.note_field = form['rus_%s_note' % rus.pk]
        context_data['rus_list'] = self.rus_list
        context_data['display_rus_list'] = self.handout.kind == u'subset'


        return context_data

    def form_valid(self, form):
        from django.db import transaction
        with transaction.commit_on_success():
            data = form.cleaned_data
            self.handout_response.note = data['note']
            self.handout_response.save()
            for rus in self.rus_list:
                rus.rus_response.checkmark = data['rus_%s_checkmark' % rus.pk]
                rus.rus_response.note = data['rus_%s_note' % rus.pk]
                rus.rus_response.save()

        return HttpResponseRedirect(reverse('handout_response', kwargs=self.kwargs))

    def form_invalid(self, form):
        print form.errors
        return self.render_to_response(self.get_context_data(form=form, form_error=True))

class HandoutResponseDeleteView(TemplateView):
    template_name = 'reg/handout_response_delete.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            handout = Handout.objects.get(
                    year=YEAR, pk=kwargs['handout'])
            rusclass = RusClass.objects.get(
                    year=YEAR, handle__exact=kwargs['rusclass'])
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

        return super(HandoutResponseDeleteView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(HandoutResponseDeleteView, self).get_context_data(**kwargs)

        context_data['handout'] = self.handout
        context_data['rusclass'] = self.rusclass
        context_data['handout_response'] = self.handout_response

        return context_data

    def post(self, request, *args, **kwargs):
        HandoutRusResponse.objects.filter(handout=self.handout, rus__rusclass=self.rusclass).delete()
        self.handout_response.delete()
        return HttpResponseRedirect(reverse('handout_list'))

class HandoutSummaryView(TemplateView):
    def get_template_names(self):
        kind = self.get_handout().kind
        if kind == u'subset':
            return ['reg/handout_summary.html']
        elif kind == u'note':
            return ['reg/handout_notes.html']
        else:
            raise AssertionError("Unknown handout kind")

    def get_handout(self):
        if not hasattr(self, '_handout'):
            self._handout = get_object_or_404(Handout, pk__exact=self.kwargs['handout'])
        return self._handout

    def get_classes(self):
        handout = self.get_handout()
        year = handout.year
        rusclasses = RusClass.objects.filter(year__exact=year)
        responses = {response.rusclass.pk: response
                for response in HandoutClassResponse.objects.filter(handout=handout)}

        all_russes = list(Rus.objects
                .filter(rusclass__in=rusclasses)
                .select_related('rusclass', 'profile', 'profile__user')
                .order_by('profile__studentnumber')
                )

        for rusclass in rusclasses:
            rusclass.russes = [rus for rus in all_russes if rus.rusclass.pk == rusclass.pk]
            rusclass.rus_total_count = len(rusclass.russes)
            if rusclass.pk in responses:
                rusclass.response = responses[rusclass.pk]
                rusclass.has_response = True
                response_queryset = HandoutRusResponse.objects.filter(
                        handout=handout,
                        rus__rusclass=rusclass).select_related('rus', 'rus__rusclass', 'rus__profile', 'rus__profile__user')
                rusclass.rus_checked_count = (response_queryset
                        .filter(checkmark=True).count())
                responses = {r.rus.pk: r for r in response_queryset}
                for rus in rusclass.russes:
                    if rus.pk in responses:
                        rus.response = responses[rus.pk]
            else:
                rusclass.has_response = False
                rusclass.rus_checked_count = 0

        return rusclasses

    def get_context_data(self, **kwargs):
        context_data = super(HandoutSummaryView, self).get_context_data(**kwargs)

        context_data['handout'] = self.get_handout()
        context_data['classes'] = self.get_classes()
        context_data['class_total_count'] = len(context_data['classes'])
        context_data['class_response_count'] = len(
                [c for c in context_data['classes'] if c.has_response])
        context_data['rus_checked_count'] = sum(r.rus_checked_count
                for r in context_data['classes'])
        context_data['rus_total_count'] = sum(r.rus_total_count
                for r in context_data['classes'])

        return context_data


class RusInfoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        rus_list = kwargs.pop('rus_list')
        super(RusInfoForm, self).__init__(*args, **kwargs)

        for rus in rus_list:
            self.fields['rus_%s_password' % rus.pk] = \
                    forms.CharField(required=False, widget=forms.PasswordInput())
            self.fields['rus_%s_email' % rus.pk] = \
                    forms.CharField(required=False)
            self.fields['rus_%s_phone' % rus.pk] = \
                    forms.CharField(required=False)

class RusInfoView(FormView):
    form_class = RusInfoForm
    template_name = 'reg/rusinfo_form.html'

    def get_form_kwargs(self):
        kwargs = super(RusInfoView, self).get_form_kwargs()
        kwargs['rus_list'] = self.rus_list
        return kwargs

    def get_initial(self):
        data = {}

        for rus in self.rus_list:
            data['rus_%s_email' % rus.pk] = rus.profile.user.email
            data['rus_%s_phone' % rus.pk] = rus.profile.phone

        return data

    def dispatch(self, request, handle):
        try:
            d = user_tutor_data(request.user)
        except NotTutor:
            return tutor_required_error(request)
        if not d.tutor:
            return tutor_required_error(request)

        self.rusclass = get_object_or_404(RusClass, handle__exact=handle, year__exact=YEAR)
        if not d.tutor.can_manage_rusclass(self.rusclass):
            return tutorbest_required_error(request)

        self.rus_list = self.get_rus_list()

        return super(RusInfoView, self).dispatch(request, handle=handle)

    def get_rus_list(self):
        return (Rus.objects.filter(rusclass=self.rusclass)
                .order_by('profile__studentnumber')
                .select_related('profile', 'profile__user'))

    def get_context_data(self, **kwargs):
        context_data = super(RusInfoView, self).get_context_data(**kwargs)
        form = context_data['form']
        for rus in self.rus_list:
            rus.email_field = form['rus_%s_email' % rus.pk]
            rus.phone_field = form['rus_%s_phone' % rus.pk]
            rus.password_field = form['rus_%s_password' % rus.pk]
        context_data['rus_list'] = self.rus_list
        context_data['rusclass'] = self.rusclass
        return context_data

    def form_valid(self, form):
        from django.db import transaction

        changes = 0
        with transaction.commit_on_success():
            data = form.cleaned_data
            for rus in self.rus_list:
                in_password = data['rus_%s_password' % rus.pk]
                in_email = data['rus_%s_email' % rus.pk]
                in_phone = data['rus_%s_phone' % rus.pk]

                if in_password:
                    rus.profile.user.set_password(in_password)
                    rus.profile.user.save()
                    changes += 1

                if in_email != rus.profile.user.email:
                    rus.profile.user.email = in_email
                    rus.profile.user.save()
                    changes += 1

                if in_phone != rus.profile.phone:
                    rus.profile.phone = in_phone
                    rus.profile.save()
                    changes += 1

        return self.render_to_response(self.get_context_data(form=form, form_saved=True, changes=changes))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form, form_errors=True))
