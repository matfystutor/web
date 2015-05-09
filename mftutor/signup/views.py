from __future__ import unicode_literals

import csv
import json

from django.views.generic import UpdateView, TemplateView, FormView

from mftutor.signup.forms import SignupImportForm
from mftutor.signup.models import TutorApplication, TutorApplicationGroup

class SignupImportView(FormView):
    form_class = SignupImportForm

    template_name = 'signup/import.html'

    def form_valid(self, form):
        text = form.cleaned_data['text']

        lines = text.encode('utf-8').splitlines()
        reader = iter(csv.reader(lines, dialect='excel-tab'))
        header = [c.decode('utf-8') for c in next(reader)]
        result = []
        for row in reader:
            values = [c.decode('utf-8') for c in row]
            result.append(dict(zip(header, values)))
        return self.render_to_response(
            self.get_context_data(form=form, result=json.dumps(result, indent=0)))
