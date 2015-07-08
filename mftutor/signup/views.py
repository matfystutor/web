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
        header = sorted(result[0].keys())
        return self.render_to_response(
            self.get_context_data(
                form=form, header=json.dumps(header, indent=0),
                result=json.dumps(result, indent=0, sort_keys=True)))
