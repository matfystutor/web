# encoding: utf-8
from django import forms
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormMixin, ProcessFormView
from django.forms.formsets import formset_factory, BaseFormSet
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from ...settings import YEAR
from ...activation.models import ProfileActivation
from ..models import Tutor, TutorGroup, TutorProfile

def classy(cl, size=10):
    return forms.TextInput(attrs={'class':cl, 'size':size})

class TutorForm(forms.Form):
    pk = forms.IntegerField(widget=forms.HiddenInput, required=False, label='')
    first_name = forms.CharField(label='Fornavn', required=False, widget=classy('first_name'))
    last_name = forms.CharField(label='Efternavn', required=False, widget=classy('last_name'))
    studentnumber = forms.CharField(label='Årskort', widget=classy('studentnumber', 7))
    study = forms.CharField(label='Studium', widget=classy('study', 7))
    email = forms.EmailField(label='Email', required=False, widget=classy('email', 25))
    groups = forms.ModelMultipleChoiceField(label='Grupper', queryset=TutorGroup.objects.filter(visible=True), required=False)

    def clean_pk(self):
        data = self.cleaned_data['pk']
        if data is not None:
            t = Tutor.objects.filter(pk=data, year=YEAR)
            if t.count == 0:
                raise forms.ValidationError('Tutor med dette interne ID findes ikke.')
        return data

TutorFormSet = formset_factory(TutorForm, extra=50)

class TutorAdminView(ProcessFormView, FormMixin, TemplateResponseMixin):
    form_class = TutorFormSet
    template_name = 'tutoradmin.html'

    def get_initial_for_tutor(self, tutor):
        profile = tutor.profile

        studentnumber = profile.studentnumber
        study = profile.study
        groups = tutor.groups.filter(visible=True)
        status = 'ghost'

        try:
            if profile.user:
                prev_data = profile.user
                status = 'normal'
            else:
                prev_data = ProfileActivation.objects.get(profile=profile)
                status = 'pending'
            first_name = prev_data.first_name
            last_name = prev_data.last_name
            email = prev_data.email
        except ProfileActivation.DoesNotExist:
            first_name = ''
            last_name = ''
            email = ''

        return {
            'pk': tutor.pk,
            'first_name': first_name,
            'last_name': last_name,
            'studentnumber': studentnumber,
            'study': study,
            'email': email,
            'groups': groups,
        }

    def get_initial(self):
        tutors = Tutor.objects.filter(year=YEAR).select_related()
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

            in_first_name = data['first_name']
            in_last_name = data['last_name']
            in_studentnumber = data['studentnumber']
            in_study = data['study']
            in_email = data['email']
            in_groups = data['groups']

            in_data = {
                'first_name': in_first_name,
                'last_name': in_last_name,
                'studentnumber': in_studentnumber,
                'study': in_study,
                'email': in_email,
                'groups': in_groups,
            }

            profile = None
            if data['pk'] is None:
                try:
                    profile = TutorProfile.objects.get(studentnumber__exact=in_studentnumber)
                    tutor = Tutor.objects.get(year=YEAR, profile=profile)
                except TutorProfile.DoesNotExist:
                    profile = TutorProfile(studentnumber=in_studentnumber)
                    profile.save()
                    tutor = Tutor(year=YEAR, profile=profile)
                except Tutor.DoesNotExist:
                    tutor = Tutor(year=YEAR, profile=profile)
                tutor.save()
                prev_data = self.get_initial_for_tutor(tutor)
                if not in_first_name: data['first_name'] = in_first_name = prev_data['first_name']
                if not in_last_name: data['last_name'] = in_last_name = prev_data['last_name']
                if not in_email: data['email'] = in_email = prev_data['email']
                if not in_study: data['study'] = in_study = prev_data['study']
                if not in_groups: data['groups'] = in_groups = prev_data['groups']

            else:
                tutor = Tutor.objects.select_related().get(pk=data['pk'], year=YEAR)
                profile = tutor.profile

                prev_data = self.get_initial_for_tutor(tutor)

                if in_data == prev_data:
                    continue

            try:
                if profile.user:
                    data_origin = profile.user
                else:
                    data_origin = ProfileActivation.objects.get(profile=profile)
            except ProfileActivation.DoesNotExist:
                data_origin = ProfileActivation(profile=profile)

            if in_first_name != prev_data['first_name']:
                data_origin.first_name = in_first_name
                changes.append(u"%s: Fornavn ændret fra %s til %s"
                    % (unicode(tutor), unicode(prev_data['first_name']), unicode(in_first_name)))

            if in_last_name != prev_data['last_name']:
                data_origin.last_name = in_last_name
                changes.append(u"%s: Efternavn ændret fra %s til %s"
                    % (unicode(tutor), unicode(prev_data['last_name']), unicode(in_last_name)))

            if in_email != prev_data['email']:
                data_origin.email = in_email
                changes.append(u"%s: Email ændret fra %s til %s"
                    % (unicode(tutor), unicode(prev_data['email']), unicode(in_email)))

            if in_studentnumber != profile.studentnumber:
                changes.append(u"%s: Årskort ændret fra %s til %s"
                    % (unicode(tutor), unicode(profile.studentnumber), unicode(in_studentnumber)))
                profile.studentnumber = in_studentnumber

            if in_study != profile.study:
                changes.append(u"%s: Studium ændret fra %s til %s"
                    % (unicode(tutor), unicode(profile.study), unicode(in_study)))
                profile.study = in_study

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

            data_origin.save()
            profile.save()
            tutor.save()

        # Here, we throw away the formset and instead get a fresh form
        formset = TutorFormSet(initial=self.get_initial())
        ctxt = self.get_context_data(form=formset, changes=changes)

        return self.render_to_response(ctxt)

    def form_invalid(self, formset):
        return self.render_to_response(self.get_context_data(form=formset))
