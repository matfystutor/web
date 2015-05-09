from __future__ import unicode_literals

import re
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
        text = re.sub(r'\r\n|\r|\n', '\n', text)

        lines = text.encode('utf-8').splitlines(True)
        reader = iter(csv.reader(lines, dialect='excel-tab'))
        header = [c.decode('utf-8') for c in next(reader)]
        expected_header = [
            "Tidspunkt",
            "Navn",
            "",
            "Mobil",
            "\u00c5rskortnummer",
            "E-mail-adresse",
            "Studieretning",
            "",
            "Antal \u00e5r som tutor",
            "Hvorn\u00e5r var du rus p\u00e5 mat/fys?",
            "Buret",
            "1.",
            "2.",
            "3.",
            "4.",
            "5.",
            "6.",
            "7.",
            "8.",
            "Kendskab til LaTeX",
            "Bem\u00e6rkninger",
        ]
        result = []
        for row in reader:
            values = [c.decode('utf-8') for c in row]
            result.append(dict(zip(header, values)))
        return self.render_to_response(
            self.get_context_data(form=form, header=json.dumps(header, indent=0), result=json.dumps(result, indent=0)))
