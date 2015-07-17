# encoding: utf-8

from __future__ import unicode_literals

from django.shortcuts import redirect
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.views.generic import TemplateView, View
from django.http import HttpResponseRedirect

from mftutor.tutor.models import TutorProfile, Tutor, Rus


class LogoutView(View):
    def post(self, request):
        logout(request)
        try:
            return HttpResponseRedirect(request.POST['next'])
        except KeyError:
            return redirect('news')


class LoginView(TemplateView):
    template_name = 'login_form.html'

    def get_user(self, login_name):
        if not login_name:
            return None

        try:
            return User.objects.get(pk=int(login_name))
        except User.DoesNotExist:
            pass
        except ValueError:
            pass

        try:
            return User.objects.get(username=login_name)
        except User.DoesNotExist:
            pass

        try:
            return TutorProfile.objects.get(email=login_name).user
        except TutorProfile.DoesNotExist:
            pass

        try:
            return TutorProfile.objects.get(studentnumber=login_name).user
        except TutorProfile.DoesNotExist:
            pass

    def post(self, request):
        login_name = request.POST['username']
        user = self.get_user(login_name)

        if user is None:
            context_data = self.get_context_data(error_code='nouser')
            return self.render_to_response(context_data)

        username = user.username
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is None:
            context_data = self.get_context_data(error_code='badpass')
            return self.render_to_response(context_data)

        try:
            profile = user.tutorprofile
        except TutorProfile.DoesNotExist:
            context_data = self.get_context_data(error_code='notutorprofile')
            return self.render_to_response(context_data)

        try:
            tutor = profile.tutor_set.get(year=request.year)
        except Tutor.DoesNotExist:
            tutor = None

        try:
            rus = profile.rus_set.get(year=request.rusyear)
        except Rus.DoesNotExist:
            rus = None

        if not tutor and not rus:
            context_data = self.get_context_data(error_code='noyear')
            return self.render_to_response(context_data)

        login(request, user)
        if rus and not tutor:
            return redirect('rus_start')
        try:
            return HttpResponseRedirect(request.POST['next'])
        except KeyError:
            return redirect('news')

    def get_context_data(self, **kwargs):
        error_code = kwargs.pop('error_code', '')

        context_data = super(LoginView, self).get_context_data(**kwargs)

        errors = {
            'nouser': 'Forkert brugernavn.',
            'badpass': 'Forkert kodeord.',
            'djangoinactive': 'Din bruger er inaktiv.',
            'notutorprofile': 'Din bruger har ingen tutorprofil.',
            'notutoryear': 'Du er ikke tutor i år.',
            'noyear': 'Du er ikke tutor eller rus i år.',
        }

        context_data['error'] = errors.get(error_code, '')

        return context_data


login_view = LoginView.as_view()
logout_view = LogoutView.as_view()
