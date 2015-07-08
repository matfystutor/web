# vim: set fileencoding=utf8:
from __future__ import unicode_literals

import re
import csv

from django import forms
from django.core.exceptions import ValidationError


class SignupImportForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)

    def clean(self):
        """
        We allow reordering the columns in the Google Forms spreadsheet
        containing the responses.
        We discard data for columns named "", "Tidspunkt" or "Timestamp".
        """
        text = self.cleaned_data['text']
        text = re.sub(r'\r\n|\r|\n', '\n', text)

        lines = text.encode('utf-8').splitlines(True)
        reader = iter(csv.reader(lines, dialect='excel-tab'))
        header = [c.decode('utf-8') for c in next(reader)]

        expected_header = set([
            "Navn",
            "Mobil",
            "\u00c5rskortnummer",
            "E-mail-adresse",
            "Studieretning",
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
        ])
        ignored_fields = set(['', 'Tidspunkt', 'Timestamp'])

        header_set = set(header) - ignored_fields

        if not header_set.issubset(expected_header):
            raise ValidationError(
                "Ugyldige header-felter i CSV data: %r" %
                (sorted(header_set - expected_header),))
        elif not expected_header.issubset(header_set):
            raise ValidationError(
                "Manglende header-felter i CSV data: %r" %
                (sorted(expected_header - header_set),))

        result = []
        for row in reader:
            values = [c.decode('utf-8').strip() for c in row]
            if not any(values):
                # Skip rows containing only blanks
                continue

            row_dict = dict(zip(header, values))
            # Remove any ignored fields present in header
            for h in ignored_fields:
                row_dict.pop(h, None)

            result.append(row_dict)

        return {
            'applications': result
        }
