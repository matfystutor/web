from django import forms
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.views.generic.base import TemplateResponseMixin
from ..news.views import BaseNewsView
from ..settings import YEAR
from ..tutor.auth import user_tutor_data, user_rus_data, NotTutor
from ..tutor.models import Tutor, Rus, RusClass

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
                    self.rusclass.get_tutors(),
                    key=lambda o: o.profile.get_full_name())
            context_data['rusclass_russes'] = sorted(
                    self.rusclass.get_russes(),
                    key=lambda o: o.profile.get_full_name())

        if self.form is not None:
            context_data['my_info_form'] = self.form

        return context_data


class RusClassView(TemplateView):
    template_name = 'rus/rusclass.html'

    def get_rusclass_list(self):
        from django.db.models import Count
        return (RusClass.objects
                .filter(year=YEAR)
                .annotate(num_russes=Count('rus'))
                .exclude(num_russes=0))

    def get_context_data(self, **kwargs):
        context_data = super(RusClassView, self).get_context_data(**kwargs)
        context_data['rusclass_list'] = self.get_rusclass_list()
        return context_data


class RusClassDetailView(RusClassView):
    def get(self, request, handle):
        self.rusclass = self.get_rusclass(handle)
        is_logged_in = False

        try:
            rus_data = user_rus_data(request.user)
            is_logged_in = True
        except NotTutor:
            pass
        try:
            tutor_data = user_tutor_data(request.user)
            is_logged_in = True
        except NotTutor:
            pass

        return self.render_to_response(self.get_context_data(is_logged_in=is_logged_in))

    def get_rusclass(self, handle):
        return get_object_or_404(RusClass, handle=handle)

    def get_rus_list(self):
        return self.rusclass.get_russes().order_by('profile__name')

    def get_tutor_list(self):
        return self.rusclass.get_tutors().order_by('profile__name')

    def get_context_data(self, **kwargs):
        is_logged_in = kwargs.pop('is_logged_in')
        context_data = super(RusClassDetailView, self).get_context_data(**kwargs)
        context_data['rusclass'] = self.rusclass
        if is_logged_in:
            context_data['rus_list'] = self.get_rus_list()
            context_data['tutor_list'] = self.get_tutor_list()
            context_data['show_details'] = True
        else:
            context_data['rus_names'] = [rus.profile.name for rus in self.get_rus_list()]
            context_data['tutor_names'] = [tutor.profile.name for tutor in self.get_tutor_list()]
            context_data['show_details'] = False
        return context_data
