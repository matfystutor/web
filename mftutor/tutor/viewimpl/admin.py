# encoding: utf-8
from django import forms
import django.forms
from django.views.generic import FormView
from django.forms.formsets import formset_factory, BaseFormSet
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from ..models import Tutor, TutorGroup, TutorProfile, RusClass, BoardMember

def classy(cl, size=10):
    return forms.TextInput(attrs={'class':cl, 'size':size})


class GroupModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.handle


class TutorForm(forms.Form):
    pk = forms.IntegerField(widget=forms.HiddenInput, required=False, label='')
    profile_pk = forms.IntegerField(widget=forms.HiddenInput, required=False, label='')
    name = forms.CharField(label='Navn', required=False, widget=classy('name'))
    studentnumber = forms.CharField(label='Årskort', widget=classy('studentnumber', 7))
    study = forms.CharField(label='Studium', widget=classy('study', 7))
    email = forms.EmailField(label='Email', required=False, widget=classy('email', 25))

    def clean_pk(self):
        data = self.cleaned_data['pk']
        if data is not None:
            t = Tutor.objects.filter(pk=data, year=self.year)
            if t.count == 0:
                raise forms.ValidationError('Tutor med dette interne ID findes ikke.')
        return data


class TutorFormSet(BaseFormSet):
    form = TutorForm
    extra = 50
    can_order = False
    can_delete = False
    min_num = 0
    max_num = 1000
    absolute_max = 2000
    validate_min = False
    validate_max = False

    def __init__(self, **kwargs):
        self.year = kwargs.pop('year')
        super(TutorFormSet, self).__init__(**kwargs)

    def add_fields(self, form, index):
        super(TutorFormSet, self).add_fields(form, index)
        form.year = self.year
        form.fields['rusclass'] = forms.ModelChoiceField(
            label='Rushold', required=False,
            queryset=RusClass.objects.filter(year__exact=self.year))
        form.fields['groups'] = GroupModelMultipleChoiceField(
            label='Grupper', required=False,
            queryset=TutorGroup.objects.filter(visible=True, year=self.year))


class TutorAdminView(FormView):
    form_class = TutorFormSet
    template_name = 'tutoradmin.html'

    def get_initial_for_tutor(self, tutor):
        profile = tutor.profile

        name = profile.name
        studentnumber = profile.studentnumber
        study = profile.study
        email = profile.email
        rusclass = tutor.rusclass
        groups = tutor.groups.filter(visible=True)

        return {
            'pk': tutor.pk,
            'profile_pk': profile.pk,
            'name': name,
            'studentnumber': studentnumber,
            'study': study,
            'email': email,
            'rusclass': rusclass,
            'groups': groups,
        }

    def get_form_kwargs(self):
        kwargs = super(TutorAdminView, self).get_form_kwargs()
        kwargs['year'] = self.request.year
        return kwargs

    def get_initial(self):
        tutors = Tutor.objects.filter(year=self.request.year)
        tutors = tutors.select_related('profile')
        result = []
        for tutor in tutors:
            result.append(self.get_initial_for_tutor(tutor))

        return result

    def get_success_url(self):
        return reverse('tutor_admin')

    def form_valid(self, formset):
        changes = []

        cleaned_data = formset.cleaned_data

        for data in formset.cleaned_data:
            if data == {}:
                continue

            in_name = data['name']
            in_studentnumber = data['studentnumber']
            in_study = data['study']
            in_email = data['email']
            in_rusclass = data['rusclass']
            in_groups = data['groups']

            in_data = {
                'name': in_name,
                'studentnumber': in_studentnumber,
                'study': in_study,
                'email': in_email,
                'rusclass': in_rusclass,
                'groups': in_groups,
            }

            profile = None
            if data['pk'] is None:
                try:
                    profile = TutorProfile.objects.get(studentnumber__exact=in_studentnumber)
                    tutor = Tutor.objects.get(year=self.request.year, profile=profile)
                except TutorProfile.DoesNotExist:
                    user = User.objects.create(username=in_studentnumber)
                    profile = TutorProfile(studentnumber=in_studentnumber, user=user)
                    profile.save()
                    tutor = Tutor(year=self.request.year, profile=profile)
                except Tutor.DoesNotExist:
                    tutor = Tutor(year=self.request.year, profile=profile)
                tutor.save()
                prev_data = self.get_initial_for_tutor(tutor)
                if not in_name: data['name'] = in_name = prev_data['name']
                if not in_email: data['email'] = in_email = prev_data['email']
                if not in_study: data['study'] = in_study = prev_data['study']
                if not in_rusclass: data['rusclass'] = in_rusclass = prev_data['rusclass']
                if not in_groups: data['groups'] = in_groups = prev_data['groups']

            else:
                tutor = Tutor.objects.select_related().get(pk=data['pk'], year=self.request.year)
                profile = tutor.profile

                prev_data = self.get_initial_for_tutor(tutor)

                if in_data == prev_data:
                    continue

            if in_name != prev_data['name']:
                profile.name = in_name
                changes.append(u"%s: Navn ændret fra %s til %s"
                    % (unicode(tutor), unicode(prev_data['name']), unicode(in_name)))
                if ' ' in in_name:
                    first_name, last_name = in_name.split(' ', 1)
                    profile.user.first_name = first_name
                    profile.user.last_name = last_name
                else:
                    profile.user.first_name = name
                    profile.user.last_name = ''
                profile.user.save()

            if in_email != prev_data['email']:
                profile.email = in_email
                changes.append(u"%s: Email ændret fra %s til %s"
                    % (unicode(tutor), unicode(prev_data['email']), unicode(in_email)))
                profile.user.email = in_email
                profile.user.save()

            if in_studentnumber != profile.studentnumber:
                changes.append(u"%s: Årskort ændret fra %s til %s"
                    % (unicode(tutor), unicode(profile.studentnumber), unicode(in_studentnumber)))
                profile.studentnumber = in_studentnumber

            if in_study != profile.study:
                changes.append(u"%s: Studium ændret fra %s til %s"
                    % (unicode(tutor), unicode(profile.study), unicode(in_study)))
                profile.study = in_study

            if in_rusclass != tutor.rusclass:
                changes.append(u"%s: Rushold ændret fra %s til %s"
                    % (unicode(tutor), unicode(tutor.rusclass), unicode(in_rusclass)))
                tutor.rusclass = in_rusclass

            in_groupset = frozenset(g.handle for g in in_data['groups'])
            prev_groupset = frozenset(g.handle for g in prev_data['groups'])
            groups_insert = in_groupset - prev_groupset
            groups_remove = prev_groupset - in_groupset
            if data['pk'] is None:
                groups_remove = []  # don't remove existing groups if entry is new

            for handle in groups_insert:
                changes.append(u"%s tilføj gruppe %s" % (unicode(tutor), handle))
                tutor.groups.add(TutorGroup.objects.get(handle=handle))

            for handle in groups_remove:
                changes.append(u"%s fjern gruppe %s" % (unicode(tutor), handle))
                tutor.groups.remove(TutorGroup.objects.get(handle=handle))

            profile.save()
            tutor.save()

        # Here, we throw away the formset and instead get a fresh form
        formset = TutorFormSet(initial=self.get_initial(), year=self.request.year)
        ctxt = self.get_context_data(form=formset, changes=changes)

        return self.render_to_response(ctxt)

    def form_invalid(self, formset):
        return self.render_to_response(self.get_context_data(form=formset))


BOARD_POSITIONS = (
    'Formand',
    'Koordineringsgruppen',
    'Koordineringsgruppen',
    'Økonomiansvarlig',
    'Praktiske grise-ansvarlig',
    'Buransvarlig',
    'Webansvarlig',
    'Menig',
    'Menig',
)


class BoardAdminForm(django.forms.Form):
    # year = django.forms.IntegerField(label=u'Tutorår')

    def __init__(self, *args, **kwargs):
        super(BoardAdminForm, self).__init__(*args, **kwargs)

        self.board_members = []
        for i, title in enumerate(BOARD_POSITIONS):
            board_member = {
                'tutor': django.forms.IntegerField(
                    required=True, label=u'Tutor'),
                'title': django.forms.CharField(
                    initial=title, required=True, label=u'Titel'),
            }
            self.board_members.append(board_member)

        for i, board_member in enumerate(self.board_members):
            self.fields['tutor%d' % i] = board_member['tutor']
            self.fields['title%d' % i] = board_member['title']

    def clean(self):
        for i, board_member in enumerate(self.board_members):
            # tutor_field = self.fields['tutor%d' % i]
            # title_field = self.fields['title%d' % i]
            # title = self.cleaned_data['title%d' % i]
            try:
                tutor_pk = self.cleaned_data['tutor%d' % i]
            except KeyError:
                continue
            if not tutor_pk:
                del self.cleaned_data['tutor%d' % i]
                del self.cleaned_data['title%d' % i]
            else:
                try:
                    self.cleaned_data['tutor%d' % i] = (
                        TutorProfile.objects.get(pk=tutor_pk))
                except TutorProfile.DoesNotExist:
                    self.errors['tutor%d' % i] = 'Denne tutorprofil findes ikke'
        return self.cleaned_data

    def __iter__(self):
        for i, bm in enumerate(self.board_members):
            yield [self['tutor%d' % i], self['title%d' % i]]



class BoardAdminView(FormView):
    form_class = BoardAdminForm
    template_name = 'boardadmin.html'

    def get_context_data(self, *args, **kwargs):
        context_data = super(BoardAdminView, self).get_context_data(
            *args, **kwargs)

        tutors = list(TutorProfile.objects.all())
        tutors = [
            {
                'pk': tp.pk,
                'name': tp.name,
            }
            for tp in tutors
        ]
        tutors.sort(key=lambda tp: tp['name'])
        import json
        context_data['tutors'] = json.dumps(tutors, indent=0)

        context_data['year'] = self.kwargs['year']

        return context_data

    def get_initial(self):
        year = int(self.kwargs['year'])
        board_members = BoardMember.objects.filter(tutor__year=year)
        initial = {}
        for i, title in enumerate(BOARD_POSITIONS):
            initial['title%d' % i] = title
        for i, board_member in enumerate(board_members):
            initial['tutor%d' % i] = board_member.tutor.profile.pk
            initial['title%d' % i] = board_member.title
        return initial

    def form_valid(self, form):
        year = int(self.kwargs['year'])
        delete_qs = BoardMember.objects.filter(tutor__year=year)
        deleted = list(delete_qs)
        deleted_dict = dict((bm.tutor.profile.pk, bm) for bm in deleted)
        delete_qs.delete()
        changed = []
        inserted = []
        for i in range(len(form.board_members)):
            try:
                profile = form.cleaned_data['tutor%d' % i]
            except KeyError:
                continue
            try:
                tutor = Tutor.objects.get(year=year, profile=profile)
            except Tutor.DoesNotExist:
                tutor = Tutor(year=year, profile=profile)
                tutor.save()
            bm = BoardMember(
                tutor=tutor,
                title=form.cleaned_data['title%d' % i],
                position=i + 1,
            )
            bm.save()
            if profile.pk in deleted_dict:
                del deleted_dict[profile.pk]
                changed.append(bm)
            else:
                inserted.append(bm)

        context_data = self.get_context_data(form=form)
        changes = []
        for pk, bm in deleted_dict.items():
            changes.append(u"%s fjernet som %s"
                           % (bm.tutor.profile.name,
                              bm.title))
        for bm in changed:
            changes.append(u"%s ændret til %s"
                           % (bm.tutor.profile.name,
                              bm.title))
        for bm in inserted:
            changes.append(u"%s tilføjet som %s"
                           % (bm.tutor.profile.name,
                              bm.title))
        context_data['changes'] = changes
        return self.render_to_response(context_data)
