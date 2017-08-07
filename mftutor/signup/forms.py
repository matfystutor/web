# vim: set fileencoding=utf8:


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
        # Read each line from the CSV
        reader = iter(csv.reader(lines, dialect='excel-tab'))
        # The first line is the CSV header
        input_header = [c.decode('utf-8') for c in next(reader)]

        header_fields = {
            "Navn": "name",
            "Mobil": "phone",
            "E-mail-adresse": "email",
            "\u00c5rskortnummer": "studentnumber",
            "Studieretning": "study",
            "Tutor type": "tutortype",
            "1": "1",
            "2": "2",
            "3": "3",
            "4": "4",
            "5": "5",
            "6": "6",
            "7": "7",
            "8": "8",
            "Kendskab til LaTeX": "latex",
            "Kommentarer": "comments",
        }
        expected_header = set(header_fields.keys())
        ignored_fields = set([
            '', 'Tidspunkt', 'Timestamp',
            'Tidsstempel', 'Sidefag',
            "Der m\u00e5 l\u00e6gges sobre billeder af mig p\u00e5 Mat/Fys-tutorgruppens facebook side",
            "Antal \u00e5r som tutor",
            "Hvorn\u00e5r var du rus p\u00e5 mat/fys?"])

        header_set = set(input_header) - ignored_fields

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
            row_values = [c.decode('utf-8').strip() for c in row]
            if not any(row_values):
                # Skip rows containing only blanks
                continue

            row_dict = {}
            for h, v in zip(input_header, row_values):
                try:
                    k = header_fields[h]
                except KeyError:
                    # Header not in header_fields: ignore value
                    continue
                row_dict[k] = v

            result.append(row_dict)

        return {
            'applications': result
        }
