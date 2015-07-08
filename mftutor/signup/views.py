from __future__ import unicode_literals

import json

from django.views.generic import UpdateView, TemplateView, FormView

from mftutor.signup.forms import SignupImportForm
from mftutor.signup.models import TutorApplication, TutorApplicationGroup


class SignupImportView(FormView):
    form_class = SignupImportForm

    template_name = 'signup/import.html'

    def form_valid(self, form):
        result = form.cleaned_data['applications']
        applications = []
        application_groups = []
        for a in result:
            o = TutorApplication()
            o.year = self.request.year
            o.name = a['name']
            o.phone = a['phone']
            o.email = a['email']
            o.studentnumber = a['studentnumber']
            o.study = a['study']
            o.previous_tutor_years = a['previous_tutor_years']
            o.rus_year = a['rus_year']
            o.new_password = False  # TODO -- should be part of application
            o.accepted = False
            o.buret = bool(a['buret'])
            o.comments = 'Kendskab til LaTeX: %s' % a['latex']
            if a['comments']:
                o.comments = '%s\n\n%s' % (o.comments, a['comments'])

            for i in range(1, 9):

                og = TutorApplicationGroup(
                    application=o, group=g, priority=i)

        return self.render_to_response(
            self.get_context_data(
                form=form, header=json.dumps(header, indent=0),
                result=json.dumps(result, indent=0, sort_keys=True)))
