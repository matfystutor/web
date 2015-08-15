import re
import json

from django.template.response import TemplateResponse
from django import forms
from django.views.generic import FormView

from mftutor.tutor.models import RusClass, TutorProfile


class TutorListForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)

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


class TutorListView(FormView):
    template_name = 'rusclass/tutorhold.html'
    form_class = TutorListForm

    def form_valid(self, form):
        template_name = "rusclass/tutorhold.tex"

        rusclass_list = []
        y = self.request.year
        for c in form.cleaned_data['text']:
            rc = RusClass.objects.create_from_handle(y, c['handle'])
            tutors = [TutorProfile.objects.get(studentnumber=sn)
                      for sn in c['tutors']]
            rusclass_list.append({
                'name': rc,
                'tutors': tutors,
            })

        context = {
            'rusclass_list': rusclass_list,
        }

        return TemplateResponse(
            request=self.request,
            template=template_name,
            context=context,
            content_type='text/plain; charset=utf-8',
        )
