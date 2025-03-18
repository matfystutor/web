# vim:set fileencoding=utf-8:

import re
import json

from django.http.response import HttpResponse
from django.template.response import TemplateResponse
from django import forms
from django.views.generic import FormView, TemplateView

from mftutor.tutor.models import RusClass, TutorProfile


class TutorListForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    pdf = forms.BooleanField(required=False)
    recipients = forms.BooleanField(required=False)
    contact = forms.BooleanField(required=False)
    assign_tutors = forms.BooleanField(required=False)

    def clean_text(self):
        text = self.cleaned_data['text']

        regex = r'("[0-9 ]+")\.split\(\)'

        def repl(mo):
            ss = json.loads(mo.group(1))
            return json.dumps(ss.split())

        text = re.sub(regex, repl, text)
        try:
            o = json.loads(text.strip())
        except ValueError as e:
            raise forms.ValidationError("Invalid JSON: %s" % (e,))

        if not isinstance(o, list):
            raise forms.ValidationError("Input is not a list")

        keys = frozenset('tutors handle'.split())
        for i, e in enumerate(o):
            if not isinstance(e, dict):
                raise forms.ValidationError("Input entry %d is not a dict" % i)
            k = frozenset(e.keys())
            if not keys.issubset(k):
                raise forms.ValidationError(
                    "Input entry %d is missing keys: %s" % (i, keys - k))
            if not k.issubset(keys):
                raise forms.ValidationError(
                    "Input entry %d has unknown keys: %s" % (i, k - keys))
            tutors = e['tutors']
            handle = e['handle']
            if not isinstance(tutors, list):
                raise forms.ValidationError("%d.tutors is not a list" % i)
            if not isinstance(handle, str):
                raise forms.ValidationError("%d.handle is not a string" % i)
            for j, a in enumerate(tutors):
                if not isinstance(a, str):
                    raise forms.ValidationError(
                        "%d.tutors.%d is not a string" % (i, j))
        return o

    def clean(self):
        cleaned_data = self.cleaned_data
        options = 'pdf recipients contact assign_tutors'.split()
        choices = [cleaned_data[o] for o in options]
        if sum(choices) != 1:
            raise forms.ValidationError(
                'Du skal vælge noget')


class TutorListView(FormView):
    template_name = 'rusclass/tutorhold.html'
    form_class = TutorListForm

    def form_valid(self, form):
        rusclass_list = []
        special_list = []
        year = self.request.year

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
                None, 'Ukendte årskortnumre: %s' % ', '.join(missing))
            return self.form_invalid(form)

        for c in form.cleaned_data['text']:
            tutors = [tutor_dict[sn] for sn in c['tutors']]
            try:
                rc = RusClass.objects.create_from_handle(year, c['handle'])
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
        elif form.cleaned_data['contact']:
            return self.generate_contact(rusclass_list)
        elif form.cleaned_data['assign_tutors']:
            return self.assign_tutors(rusclass_list)
        else:
            form.add_error(None, 'No choice')
            return self.form_invalid(form)

    def generate_tex(self, rusclass_list):
        year = self.request.year
        rusclass_list = sorted(rusclass_list, key=lambda x: x['name'].handle)
        for rc in rusclass_list:
            rc['tutors'] = sorted(rc['tutors'], key=lambda x: x.name)
        template_name = "rusclass/tutorhold.tex"

        context = {
            'rusclass_list': rusclass_list,
            'year': year,
        }

        return TemplateResponse(
            request=self.request,
            template=template_name,
            context=context,
            content_type='text/plain; charset=utf-8',
        )

    def generate_contact(self, rusclass_list):
        year = self.request.year
        rusclass_list = sorted(rusclass_list, key=lambda x: x['name'].handle)
        for rc in rusclass_list:
            rc['tutors'] = sorted(rc['tutors'], key=lambda x: x.name)
        template_name = "rusclass/tutorhold_contact.html"

        context = {
            'rusclass_list': rusclass_list,
            'year': year,
        }

        return TemplateResponse(
            request=self.request,
            template=template_name,
            context=context,
            content_type='text/html; charset=utf-8',
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

    def assign_tutors(self, rusclass_list):
        for o in rusclass_list:
            rc = o['name']
            if not rc.pk:
                try:
                    rc = RusClass.objects.get(
                        year=rc.year, handle=rc.handle)
                except RusClass.DoesNotExist:
                    rc.save()
            profiles = o['tutors']
            tutors = [tp.tutor_set.get(year=self.request.year)
                      for tp in profiles]
            for t in tutors:
                t.rusclass = rc
                t.save()

        return HttpResponse("Succes!")


class RusClassTexView(TemplateView):
    template_name = 'rusclass/rusclass.tex'

    def get_context_data(self, **kwargs):
        context_data = super(RusClassTexView, self).get_context_data(**kwargs)

        rusclass_list = RusClass.objects.filter(year=self.request.year)
        rusclass_list = rusclass_list.prefetch_related('rus_set__profile')
        context_data['rusclass_list'] = rusclass_list

        return context_data
