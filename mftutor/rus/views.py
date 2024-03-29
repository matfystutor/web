# vim:fileencoding=utf-8:
from django import forms
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, FormView
from django.views.generic.base import TemplateResponseMixin
from django.contrib.auth.forms import PasswordChangeForm
from ..news.views import BaseNewsView
from ..tutor.models import RusClass

class RusNewsView(BaseNewsView, TemplateResponseMixin):
    template_name = 'rus/nyheder.html'

    def get_group_handle(self):
        return 'rus'


class MyInfoForm(forms.Form):
    phone = forms.CharField()
    email = forms.EmailField()

class RusStartView(TemplateView):
    template_name = 'rus/start.html'

    def get(self, request):
        self.form = None
        if request.rus:
            in_phone = request.tutorprofile.phone
            in_email = request.tutorprofile.email
            if in_phone == '' or in_email == '':
                self.form = MyInfoForm(initial={'phone': in_phone, 'email': in_email})

        return self.render_to_response(self.get_context_data())

    def post(self, request):
        form = self.form = MyInfoForm(request.POST)
        if form.is_valid():
            request.tutorprofile.phone = form.cleaned_data['phone']
            request.tutorprofile.email = form.cleaned_data['email']
            request.tutorprofile.save()
            return self.render_to_response(self.get_context_data(form_saved=True))
        else:
            return self.render_to_response(self.get_context_data(form_errors=True))

    def get_context_data(self, **kwargs):
        context_data = super(RusStartView, self).get_context_data(**kwargs)

        if self.request.rus:
            rusclass = context_data['rusclass'] = self.request.rus.rusclass
            context_data['rusclass_tutors'] = sorted(
                    rusclass.get_tutors(),
                    key=lambda o: o.profile.get_full_name())
            context_data['rusclass_russes'] = sorted(
                    rusclass.get_russes(),
                    key=lambda o: o.profile.get_full_name())

        if self.form is not None:
            context_data['my_info_form'] = self.form

        return context_data


class RusClassView(TemplateView):
    template_name = 'rus/rusclass.html'

    def get_rusclass_list(self):
        from django.db.models import Count
        return (RusClass.objects
                .filter(year=self.request.rusyear)
                .annotate(num_russes=Count('rus'), num_tutors=Count('tutor'))
                .filter(num_russes__gt=0))

    def get_context_data(self, **kwargs):
        context_data = super(RusClassView, self).get_context_data(**kwargs)
        context_data['rusclass_list'] = self.get_rusclass_list()
        return context_data


class RusClassDetailView(RusClassView):
    def get(self, request, handle):
        self.rusclass = self.get_rusclass(handle)
        is_logged_in = bool(request.tutor or request.rus)
        return self.render_to_response(self.get_context_data(is_logged_in=is_logged_in))

    def get_rusclass(self, handle):
        if handle == 'tk1':
            return RusClass(year=self.request.rusyear, handle=handle, internal_name='Teknokemi 1', official_name='TÅ1')
        return get_object_or_404(RusClass, year=self.request.rusyear, handle=handle)

    def get_rus_list(self):
        return self.rusclass.get_russes().order_by('profile__name')

    def get_tutor_list(self):
        return self.rusclass.get_tutors().order_by('profile__name')

    def get_context_data(self, **kwargs):
        is_logged_in = kwargs.pop('is_logged_in')
        context_data = super(RusClassDetailView, self).get_context_data(**kwargs)
        context_data['rusclass'] = self.rusclass
        if self.rusclass.handle == 'tk1':
            j = 'Jeppe'
            hj = 'Henrijeppe'
            context_data['rus_names'] = (j, j, hj, j, hj, j, j, hj, hj, j, hj,
                    hj, hj, 'JepPer', j, hj, j, j, j, j, j, hj, j, j, hj)
            context_data['tutor_names'] = (
                    'Jakob Schultz-Nielsen',
                    'Kenneth S. Bøgh',
                    'Mads Baggesen',
                    'Morten N. Pløger',
                    )
            context_data['show_details'] = False
        elif is_logged_in:
            context_data['rus_list'] = self.get_rus_list()
            context_data['tutor_list'] = self.get_tutor_list()
            context_data['show_details'] = True
        else:
            context_data['rus_names'] = [rus.profile.name for rus in self.get_rus_list()]
            context_data['tutor_names'] = [tutor.profile.name for tutor in self.get_tutor_list()]
            context_data['show_details'] = False
        return context_data


class RusClassDetailsPrintView(RusClassDetailView):
    template_name = 'rus/rusclass.tex'


class ProfileForm(forms.Form):
    street = forms.CharField(label='Adresse', required=False)
    city = forms.CharField(label='Postnr. og by', required=False)
    phone = forms.CharField(label='Telefon', required=False)


class ProfileView(FormView):
    form_class = ProfileForm
    template_name = 'rus/profileform.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.rus:
            return self.render_to_response(self.get_context_data(error='Du er ikke rus!', form=ProfileForm()))
        return super(ProfileView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        profile = self.request.tutorprofile

        return {
            'street': profile.street,
            'city': profile.city,
            'phone': profile.phone,
        }

    def form_valid(self, form):
        profile = self.request.tutorprofile
        data = form.cleaned_data
        with transaction.atomic():
            profile.street = data['street']
            profile.city = data['city']
            profile.phone = data['phone']
            profile.save()
            profile.user.save()
        return self.render_to_response(self.get_context_data(form=form, saved=True))


class RusPasswordChangeView(FormView):
    form_class = PasswordChangeForm
    template_name = 'rus/password_change_form.html'

    def form_invalid(self, form):
        return super(RusPasswordChangeView, self).form_invalid(form)

    def form_valid(self, form):
        form.save()
        return self.render_to_response(self.get_context_data(success=True))

    def get_context_data(self, **kwargs):
        context_data = super(RusPasswordChangeView, self).get_context_data(**kwargs)
        return context_data

    def get_form_kwargs(self):
        kwargs = super(RusPasswordChangeView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class TutorListView(TemplateView):
    template_name = 'rus/tutor_list_view.html'

    def get_context_data(self, **kwargs):
        context_data = super(TutorListView, self).get_context_data(**kwargs)

        year = self.request.year
        qs = RusClass.objects.filter(year=year)
        qs = qs.prefetch_related('tutor_set__profile')

        rusclass_list = []
        for rc in qs:
            rc.tutors = [tu.profile for tu in rc.tutor_set.all()]
            rusclass_list.append(rc)

        context_data['rusclass_list'] = rusclass_list
        context_data['year'] = year
        return context_data
