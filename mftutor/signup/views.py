# vim: set fileencoding=utf8:
from __future__ import unicode_literals

import json

from django.http import HttpResponseRedirect
from django.views.generic import UpdateView, TemplateView, FormView, ListView
from django.views.generic.list import MultipleObjectMixin
from django import forms
from django.core.urlresolvers import reverse
from django.db.models import Count

from mftutor.signup.forms import SignupImportForm
from mftutor.signup.models import (
    TutorApplication, TutorApplicationGroup, AssignedGroupLeader)
from mftutor.tutor.models import TutorProfile, TutorGroup, Rus, Tutor
from mftutor.tutor.views import GroupLeaderViewBase


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


class SignupImportView(FormView):
    form_class = SignupImportForm

    template_name = 'signup/import.html'

    def form_valid(self, form):
        """
        1. Generate TutorApplication objects
        2. Retrieve existing TutorProfiles based on studentnumbers
        3. Assign existing TutorProfiles
        4. Retrieve all TutorGroups
        5. Generate TutorApplicationGroup objects
        6. Save TutorApplications
        7. Save TutorApplicationGroups
        """

        result = form.cleaned_data['applications']

        # 1. Generate TutorApplication objects
        applications = []
        group_names = []
        for a in result:
            app = TutorApplication()
            app.year = self.request.year
            app.name = a['name']
            app.phone = a['phone']
            app.email = a['email']
            app.studentnumber = a['studentnumber']
            app.study = a['study']
            app.previous_tutor_years = 0
            app.rus_year = 0
            app.new_password = False  # TODO -- should be part of application
            app.buret = bool(a['buret'])
            app.comments = 'Kendskab til LaTeX: %s' % a['latex']
            if a['comments']:
                app.comments = '%s\n\n%s' % (app.comments, a['comments'])
            applications.append(app)
            if a['buret']:
                group_names.append((app, 'Buret', 0))
            for priority in range(1, 9):
                group_name = a[str(priority)]
                if group_name:
                    group_names.append((app, group_name, priority))

        # 2. Retrieve existing TutorProfiles based on studentnumbers
        studentnumbers = [app.studentnumber for app in applications]
        tutorprofiles = TutorProfile.objects.filter(
            studentnumber__in=studentnumbers)
        tp_dict = {
            tp.studentnumber: tp
            for tp in tutorprofiles
        }

        # 3. Assign existing TutorProfiles
        for app in applications:
            try:
                tp = tp_dict[app.studentnumber]
            except KeyError:
                tp = TutorProfile(
                    name=app.name,
                    phone=app.phone,
                    email=app.email,
                    study=app.study,
                    studentnumber=app.studentnumber,
                )
                tp.save()
            app.profile = tp
            try:
                rus_qs = Rus.objects.filter(profile=tp).order_by('year')
                rus = next(iter(rus_qs))
            except StopIteration:
                rus = Rus(year=0)
            app.rus_year = rus.year
            app.previous_tutor_years = len(
                Tutor.objects.filter(profile=tp, year__lt=self.request.year))

        # 4. Retrieve all TutorGroups
        tg_dict = self.get_tutorgroup_dict()

        # 5. Generate TutorApplicationGroup objects
        application_groups = []
        unknown_names = []
        for app, group_name, priority in group_names:
            try:
                group = tg_dict[group_name]
            except KeyError:
                trans_group = self.get_real_tutorgroup_name(group_name, app.study)
                if trans_group is not None:
                    try:
                        group = tg_dict[trans_group]
                    except KeyError:
                        unknown_names.append(trans_group)
                        unknown_names.append(group_name)
                        continue
                else:
                    unknown_names.append(group_name)
                    continue
            ag = TutorApplicationGroup(group=group, priority=priority)
            application_groups.append((app, ag))

        if unknown_names:
            error = (
                "Ukendte grupper: %s" %
                ', '.join(sorted(set(unknown_names))))
            form.add_error('text', error)
            return self.render_to_response(
                self.get_context_data(
                    form=form))

        # 6. Save TutorApplications
        for app in applications:
            app.save()

        # 7. Save TutorApplicationGroups
        for app, appgroup in application_groups:
            appgroup.application = app
            appgroup.save()

        return HttpResponseRedirect(reverse("signup_list"))

    def get_tutorgroup_dict(self):
        tutorgroups = TutorGroup.objects.filter(visible=True, year=self.request.year)
        tg_dict = {
            tg.name: tg
            for tg in tutorgroups
        }
        return tg_dict

    def get_real_tutorgroup_name(self, group_name, study):
        tg_dict = {}
        tg_dict['TØ i rusdagene'] = {
            'dat': 'TØ i rusdagene - datalogi',
            'it': 'TØ i rusdagene - IT',
            'mat': 'TØ i rusdagene - matematik',
            'mok': 'TØ i rusdagene - mat/øk',
            'nano': 'TØ i rusdagene - nano',
            'fys': 'TØ i rusdagene - fysik',
        }
        tg_dict['Dias'] = {
            'dat': 'Dias - CS',
            'it': 'Dias - CS',
            'mat': 'Dias - IMF',
            'mok': 'Dias - IMF',
            'nano': 'Dias - IFA',
            'fys': 'Dias - IFA',
        }
        if group_name in tg_dict:
            s = parse_study(study)
            return tg_dict[group_name][s]
        renames = [
            ('iNano-lab', 'iNANO-labrundvisning'),
            ('IFA-lab', 'IFA-Labrundvisning'),
            ('CS-lab', 'CS-labrundvisning'),
            ('Evaluering', 'Evalueringer'),
            ('Hytte', 'Hytter'),
            ('Indkøb', 'Metro'),
            ('Lokalegruppen', 'Lokale'),
            ('Lokaler', 'Lokale'),
            ('Rusguide', 'Rushåndbog'),
            ('Sportsdagsgruppen', 'Sportsdag'),
        ]
        for app_name, site_name in renames:
            if app_name == group_name:
                return site_name


class SignupListActionForm(forms.Form):
    action = forms.CharField()
    nargs = forms.CharField()
    argument0 = forms.CharField(required=False)
    argument1 = forms.CharField(required=False)

    def clean_action(self):
        action = self.cleaned_data['action']
        try:
            getattr(SignupListView, 'action_' + action)
        except AttributeError:
            raise forms.ValidationError(u'Invalid action')
        return action


class SignupListView(FormView):
    form_class = SignupListActionForm
    model = TutorApplication
    template_name = 'signup/list.html'

    def get_queryset(self):
        qs = TutorApplication.objects.filter(year=self.request.year)
        qs = qs.select_related('profile').prefetch_related(
            'tutorapplicationgroup_set',
            'tutorapplicationgroup_set__group',
            'assigned_groups',
            'groups',
        )

        profiles = [app.profile for app in qs]
        group_memberships = Tutor.groups.through.objects.filter(
            tutor__profile__in=profiles).select_related('tutor', 'tutorgroup')
        all_experience = {}
        for o in group_memberships:
            key = (o.tutor.profile_id, o.tutorgroup.handle)
            is_leader = o.tutorgroup.leader_id == o.tutor_id
            exp = all_experience.setdefault(key, [])
            exp.append((o.tutor.year, is_leader, o.tutorgroup))

        applications = list(qs)
        for app in applications:
            group_list = []
            group_ids = set()
            for g in app.tutorapplicationgroup_set.all():
                if g.group_id not in group_ids:
                    group_ids.add(g.group_id)
                    group_list.append((g.group, g.priority))

            for g in app.assigned_groups.all():
                if g not in app.groups.all():
                    group_list.append((g, None))

            app.group_list = []
            for group, priority in group_list:
                exp_key = (app.profile_id, group.handle)
                exp = all_experience.get(exp_key, [])

                experience_detail = u'\n'.join(
                    '%s %s%s' %
                    (year, group.name, ' (ansv.)' if is_leader else '')
                    for year, is_leader, group in exp)

                o = {
                    'name': group.name,
                    'handle': group.handle,
                    'priority': priority,
                    'pk': group.pk,
                    'experience': len(exp),
                    'experience_detail': experience_detail,
                }

                if group in app.assigned_groups.all():
                    o['assigned'] = True
                else:
                    o['assigned'] = False
                app.group_list.append(o)

        sortform = self.get_sortform()
        if sortform.is_valid():
            group_handle = sortform.cleaned_data['group']

            def app_key(app):
                a = 1
                for g in app.assigned_groups.all():
                    if g.handle == group_handle:
                        a = 0
                for i, g in enumerate(app.group_list):
                    if g['handle'] == group_handle:
                        return a, i
                return a, 100

            applications.sort(key=app_key)

        return applications

    def get_sortform(self):
        form = forms.Form(data=self.request.GET)
        choices = []
        qs = self.get_groups()
        qs = qs.annotate(num_assigned=Count('tutorapplication_assigned_set'))
        for g in qs:
            name = '(%s) %s' % (g.num_assigned or '--', g.name)
            choices.append((g.handle, name))
        form.fields['group'] = forms.ChoiceField(
            label=u'Sortér efter', choices=choices)
        return form

    def get_groups(self):
        qs = TutorGroup.objects.filter(year=self.request.year, visible=True)
        return qs

    def get_stats(self, applications):
        buret = 0
        accepted = 0
        not_accepted = 0
        num_groups = [0, 0, 0, 0]
        for app in applications:
            if app.accepted:
                accepted += 1
            else:
                not_accepted += 1

            assigned_count = 0
            b = False
            for g in app.group_list:
                if g['assigned']:
                    assigned_count += 1
                    if g['handle'] == 'buret':
                        b = True

            if assigned_count >= len(num_groups):
                assigned_count = len(num_groups) - 1

            if b:
                buret += 1
            else:
                num_groups[assigned_count] += 1

        stats = {
            'accepted': accepted,
            'not_accepted': not_accepted,
            'buret': buret,
        }
        for i, count in enumerate(num_groups):
            stats[str(i)] = count
        return stats

    def get_context_data(self, **kwargs):
        context_data = super(SignupListView, self).get_context_data(**kwargs)
        applications = self.get_queryset()
        context_data['application_list'] = applications
        context_data['groups'] = self.get_groups()
        context_data['sortform'] = self.get_sortform()
        context_data['stats'] = self.get_stats(applications)
        return context_data

    def get_success_url(self):
        return reverse('signup_list')

    def form_valid(self, form):
        action = form.cleaned_data['action']
        nargs = int(form.cleaned_data['nargs'])
        args = [form.cleaned_data['argument%s' % i] for i in range(nargs)]
        getattr(self, 'action_' + action)(*args)
        return self.render_to_response(self.get_context_data(form=form))

    def action_assign_group(self, app_id, group_id):
        app_id = int(app_id)
        group_id = int(group_id)
        ta = TutorApplication.objects.get(id=app_id)
        group = TutorGroup.objects.get(id=group_id)
        if group in ta.assigned_groups.all():
            ta.assigned_groups.remove(group)
        else:
            ta.assigned_groups.add(group)

    def action_accepted(self, argument):
        pk = int(argument)
        ta = TutorApplication.objects.get(pk=pk)
        ta.accepted = not ta.accepted
        ta.save()


class TutorGroupForm(forms.Form):
    def __init__(self, groups, year, **kwargs):
        super(TutorGroupForm, self).__init__(**kwargs)
        for group in groups:
            if group.year != year:
                name = self.get_group_field_name(group)
                self.fields[name] = forms.BooleanField(
                    label=group.name, required=False)

    @staticmethod
    def get_group_field_name(group):
        return 'field_%s' % group.pk

    def get_group_bound_field(self, group):
        return self[self.get_group_field_name(group)]

    def clean(self):
        cleaned_data = super(TutorGroupForm, self).clean()
        if not any(cleaned_data.values()):
            raise forms.ValidationError(u'Ingen grupper valgt')
        return cleaned_data


class TutorGroupView(FormView):
    template_name = 'signup/tutorgroups.html'
    form_class = TutorGroupForm

    def dispatch(self, request, *args, **kwargs):
        # Used in get_form_kwargs and get_context_data
        self.groups = self.get_groups()
        return super(TutorGroupView, self).dispatch(request, *args, **kwargs)

    def get_groups(self):
        by_handle = {}
        all_groups = TutorGroup.objects.all().order_by('year')
        for g in all_groups:
            # Overwrite older groups
            if g.year:
                by_handle[g.handle] = g
        groups = list(by_handle.values())
        groups.sort(key=lambda g: g.name)
        return groups

    def get_form_kwargs(self):
        kwargs = super(TutorGroupView, self).get_form_kwargs()
        kwargs['groups'] = self.groups
        kwargs['year'] = self.request.year
        return kwargs

    def get_initial(self):
        return {
            self.form_class.get_group_field_name(g):
            (g.year == self.request.year - 1)
            for g in self.groups
        }

    def get_context_data(self, **kwargs):
        context_data = super(TutorGroupView, self).get_context_data(**kwargs)

        form = context_data['form']
        for g in self.groups:
            if g.year != self.request.year:
                g.field = form.get_group_bound_field(g)

        context_data['groups'] = self.groups
        context_data['year'] = self.request.year
        return context_data

    def get_success_url(self):
        return reverse('signup_groups')

    def form_valid(self, form):
        data = form.cleaned_data
        new_groups = []
        for g in self.groups:
            if data.get(form.get_group_field_name(g)):
                tg = TutorGroup(
                    handle=g.handle,
                    name=g.name,
                    visible=g.visible,
                    year=self.request.year)
                new_groups.append(tg)
        for g in new_groups:
            g.save()

        return super(TutorGroupView, self).form_valid(form)


class GroupLeaderView(GroupLeaderViewBase):
    def get_groups(self):
        qs = TutorGroup.objects.filter(
            visible=True, year=self.request.year)
        qs = qs.prefetch_related('tutorapplication_assigned_set__profile')
        qs = qs.select_related('assignedgroupleader')
        groups = []
        for g in qs:
            app_qs = g.tutorapplication_assigned_set.all()
            tutors = [(app.pk, app.profile.name) for app in app_qs]
            try:
                leader = g.assignedgroupleader.application_id
            except AssignedGroupLeader.DoesNotExist:
                leader = None
            groups.append({
                'pk': g.pk,
                'name': g.name,
                'tutors': tutors,
                'leader': leader,
            })
        return groups

    def change_leaders(self, changes):
        for group, new_leader in changes:
            existing = AssignedGroupLeader.objects.filter(
                group_id=group['pk'])

            # Delete existing (if any)
            existing.delete()

            # Create new (if needed)
            if new_leader:
                n = AssignedGroupLeader(
                    group_id=group['pk'], application_id=new_leader)
                n.save()


class TutorCreateForm(forms.Form):
    def __init__(self, applications, **kwargs):
        super(TutorCreateForm, self).__init__(**kwargs)



class TutorCreateView(FormView):
    template_name = 'signup/create.html'
    form_class = TutorCreateForm

    def get_form_kwargs(self):
        kwargs = super(TutorCreateView, self).get_form_kwargs()
        kwargs["applications"] = self.get_applications()
        return kwargs

    def get_applications(self):
        qs = TutorApplication.objects.filter(year=self.request.year)
        qs = qs.select_related('profile').prefetch_related(
            'tutorapplicationgroup_set',
            'tutorapplicationgroup_set__group',
            'assigned_groups',
            'groups',
        )
        return qs

    def get_context_data(self, **kwargs):
        context_data = super(TutorCreateView, self).get_context_data(**kwargs)
        context_data['application_list'] = self.get_applications()
        return context_data

    def get_success_url(self):
        return reverse('signup_create')

    def form_valid(self, form):
        applications = self.get_applications()

        # divide into groups that match email templates
        grouped_tutors = self.divide_into_groups(applications)

        # save tutor objects
        all_accepted_tutors = []
        all_accepted_tutors += grouped_tutors["accepted"]
        all_accepted_tutors += grouped_tutors["responsable"]
        all_accepted_tutors += grouped_tutors["buret"]
        all_accepted_tutors += grouped_tutors["buret_responsable"]
        self.save_tutor_from_applications(all_accepted_tutors, dry_run=True)

        # send emails
        # TODO

        return super(TutorCreateView, self).form_valid(form)

    @staticmethod
    def divide_into_groups(applications):
        status = {
            "rejected": [],
            "accepted": [],
            "responsable": [],
            "buret": [],
            "buret_responsable": []
        }
        for application in applications:
            if not application.accepted:
                status["rejected"].append(application)
                continue
            tutor_groups = application.assigned_groups.all()

            # TODO add tutors that are responsible for a group

            if 'buret' in tutor_groups:
                status['buret'].append(application)
            else:
                status['accepted'].append(application)

        return status

    @staticmethod
    def save_tutor_from_applications(applications, dry_run=False):
        for application in applications:
            try:
                tutor = Tutor.objects.get(
                    profile=application.profile,
                    year=application.year,
                )
            except Tutor.DoesNotExist:
                tutor = Tutor(
                    profile=application.profile,
                    year=application.year,
                )
                if not dry_run:
                    tutor.save()
            if not dry_run:
                tutor.groups = application.assigned_groups.all()
                tutor.save()
