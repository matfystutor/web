from django import forms
from django.views.generic import TemplateView
from django.views.generic.base import TemplateResponseMixin
from ..news.views import BaseNewsView
from ..tutor.auth import user_tutor_data, user_rus_data, NotTutor
from ..tutor.models import Tutor, Rus

class RusNewsView(BaseNewsView, TemplateResponseMixin):
    template_name = 'rus/nyheder.html'

    def get_group_handle(self):
        return u'rus'


class MyInfoForm(forms.Form):
    phone = forms.CharField()
    email = forms.EmailField()

class RusStartView(TemplateView):
    template_name = 'rus/start.html'

    def dispatch(self, request):
        self.form = None
        try:
            d = user_rus_data(request.user)
            self.rus = d.rus
            self.rusclass = self.rus.rusclass
        except NotTutor:
            self.rus = None
            self.rusclass = None

        return super(RusStartView, self).dispatch(request)

    def get(self, request):
        if self.rus is not None:
            in_phone = self.rus.profile.phone
            in_email = self.rus.profile.email
            if in_phone == '' or in_email == '':
                self.form = MyInfoForm(initial={'phone': in_phone, 'email': in_email})

        return self.render_to_response(self.get_context_data())

    def post(self, request):
        form = self.form = MyInfoForm(request.POST)
        if form.is_valid():
            self.rus.profile.phone = form.cleaned_data['phone']
            self.rus.profile.email = form.cleaned_data['email']
            self.rus.profile.save()
            return self.render_to_response(self.get_context_data(form_saved=True))
        else:
            return self.render_to_response(self.get_context_data(form_errors=True))

    def get_context_data(self, **kwargs):
        context_data = super(RusStartView, self).get_context_data(**kwargs)

        if self.rusclass is not None:
            context_data['rusclass'] = self.rusclass
            context_data['rusclass_tutors'] = sorted(
                    Tutor.objects.filter(rusclass=self.rusclass),
                    key=lambda o: o.profile.get_full_name())
            context_data['rusclass_russes'] = sorted(
                    Rus.objects.filter(rusclass=self.rusclass),
                    key=lambda o: o.profile.get_full_name())

        if self.form is not None:
            context_data['my_info_form'] = self.form

        return context_data
