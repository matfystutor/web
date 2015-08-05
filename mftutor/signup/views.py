# vim: set fileencoding=utf8:
from __future__ import unicode_literals

import json

from django.views.generic import UpdateView, TemplateView, FormView, ListView

from mftutor.signup.forms import SignupImportForm
from mftutor.signup.models import TutorApplication, TutorApplicationGroup
from mftutor.tutor.models import TutorProfile, TutorGroup, Rus, Tutor


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
            app.previous_tutor_years = len(Tutor.objects.filter(profile=tp))

        # 4. Retrieve all TutorGroups
        tg_dict = self.get_tutorgroup_dict()

        # 5. Generate TutorApplicationGroup objects
        application_groups = []
        unknown_names = []
        for app, group_name, priority in group_names:
            try:
                group = tg_dict[group_name]
            except KeyError:
                unknown_names.append(group_name)
                continue
            if isinstance(group, dict):
                study = parse_study(app.study)
                if study is None:
                    group = next(iter(group.values()))
                else:
                    group = group[study]
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

        return self.render_to_response(
            self.get_context_data(
                form=form,
                study=json.dumps(sorted(set((a['study'].lower(), parse_study(a['study'])) for a in result))),
                result=json.dumps(result, indent=0, sort_keys=True)))

    def get_tutorgroup_dict(self):
        tutorgroups = TutorGroup.objects.filter(visible=True)
        tg_dict = {
            tg.name: tg
            for tg in tutorgroups
        }
        tg_dict['TØ i rusdagene'] = {
            'dat': tg_dict.get('TØ i rusdagene - datalogi'),
            'it': tg_dict.get('TØ i rusdagene - IT'),
            'mat': tg_dict.get('TØ i rusdagene - matematik'),
            'mok': tg_dict.get('TØ i rusdagene - mat/øk'),
            'nano': tg_dict.get('TØ i rusdagene - nano'),
            'fys': tg_dict.get('TØ i rusdagene - fysik'),
        }
        tg_dict['Dias'] = {
            'dat': tg_dict.get('Dias - CS'),
            'it': tg_dict.get('Dias - CS'),
            'mat': tg_dict.get('Dias - IMF'),
            'mok': tg_dict.get('Dias - IMF'),
            'nano': tg_dict.get('Dias - IFA'),
            'fys': tg_dict.get('Dias - IFA'),
        }
        renames = [
            ('iNano-lab', 'iNANO-labrundvisning'),
            ('IFA-lab', 'IFA-Labrundvisning'),
            ('CS-lab', 'CS-labrundvisning'),
            ('Evaluering', 'Evalueringer'),
            ('Hytte', 'Hytter'),
            ('Indkøb', 'Metro'),
            ('Lokalegruppen', 'Lokaler'),
            ('Rusguide', 'Rushåndbog'),
            ('Sportsdagsgruppen', 'Sportsdag'),
        ]
        for app_name, site_name in renames:
            if app_name not in tg_dict:
                tg_dict[app_name] = tg_dict[site_name]
        return tg_dict


class SignupListView(ListView):
    model = TutorApplication
    template_name = 'signup/list.html'
    context_object_name = 'application_list'

    def get_queryset(self):
        qs = TutorApplication.objects.filter(year=self.request.year)
        return qs.select_related('profile').prefetch_related(
            'tutorapplicationgroup_set',
            'tutorapplicationgroup_set__group',
        )
