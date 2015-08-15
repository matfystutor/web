# vim:set fileencoding=utf-8:

import re
import json

from django.template.response import TemplateResponse
from django import forms
from django.views.generic import FormView

from mftutor.tutor.models import RusClass, TutorProfile


class TutorListForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    pdf = forms.BooleanField(required=False)
    recipients = forms.BooleanField(required=False)

    def clean_text(self):
        text = self.cleaned_data['text']

        regex = r'"([0-9 ]+)"\.split\(\)'

        def repl(mo):
            return '[%s]' % ', '.join('"%s"' % s for s in mo.group(1).split())

        text = re.sub(regex, repl, text)
        try:
            o = json.loads(text.strip())
        except ValueError as e:
            raise forms.ValidationError("Invalid JSON: %s %r" % (e, text))
        return o

    def clean(self):
        cleaned_data = self.cleaned_data
        options = 'pdf recipients'.split()
        choices = [cleaned_data[o] for o in options]
        if sum(choices) != 1:
            raise forms.ValidationError(
                u'Du skal vælge noget')


class TutorListView(FormView):
    template_name = 'rusclass/tutorhold.html'
    form_class = TutorListForm

    def form_valid(self, form):
        rusclass_list = []
        special_list = []
        y = self.request.year

        studentnumbers = []
        for c in form.cleaned_data['text']:
            for sn in c['tutors']:
                studentnumbers.append(sn)

        qs = TutorProfile.objects.filter(studentnumber__in=studentnumbers)
        tutor_dict = {}
        for tp in qs:
            tutor_dict[tp.studentnumber] = tp
        missing = set(studentnumbers) - set(tutor_dict.keys())
        if missing:
            form.add_error(
                None, u'Ukendte årskortnumre: %s' % ', '.join(missing))
            return self.form_invalid(form)

        for c in form.cleaned_data['text']:
            tutors = [tutor_dict[sn] for sn in c['tutors']]
            try:
                rc = RusClass.objects.create_from_handle(y, c['handle'])
                rusclass_list.append({
                    'name': rc,
                    'tutors': tutors,
                })
            except ValueError:
                special_list.append({
                    'name': c['handle'],
                    'tutors': tutors,
                })

        if form.cleaned_data['pdf']:
            return self.generate_tex(rusclass_list)
        elif form.cleaned_data['recipients']:
            return self.generate_recipients(rusclass_list, special_list)
        else:
            form.add_error(None, u'No choice')
            return self.form_invalid(form)

    def generate_tex(self, rusclass_list):
        template_name = "rusclass/tutorhold.tex"

        context = {
            'rusclass_list': rusclass_list,
        }

        return TemplateResponse(
            request=self.request,
            template=template_name,
            context=context,
            content_type='text/plain; charset=utf-8',
        )

    def generate_recipients(self, rusclass_list, special_list):
        tutors = []
        for o in rusclass_list:
            for t in o['tutors']:
                tutors.append(t)
        special_list += [{'name': 'tutors', 'tutors': tutors}]

        template_name = "rusclass/recipients.txt"

        context = {
            'list': special_list,
        }

        return TemplateResponse(
            request=self.request,
            template=template_name,
            context=context,
            content_type='text/plain; charset=utf-8',
        )
