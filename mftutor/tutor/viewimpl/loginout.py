# encoding: utf-8
from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.core.urlresolvers import NoReverseMatch, reverse
from django.contrib.auth.models import User
from django.views.generic import TemplateView, View
from django.http import HttpResponseRedirect
from ..models import TutorProfile
from ..auth import user_tutor_data, NotTutor, user_rus_data

class LogoutView(View):
    def post(self, request):
        logout(request)
        try:
            return HttpResponseRedirect(request.POST['next'])
        except KeyError:
            return redirect('news')

class LoginView(TemplateView):
    template_name = 'login_form.html'

    def post(self, request):
        loginname = request.POST['username']
        username = None

        if username is None:
            try:
                i = int(loginname)
                u = User.objects.get(id=i)
                username = u.username
            except ValueError:
                pass
            except User.DoesNotExist:
                pass

        if username is None:
            try:
                u = User.objects.get(username=loginname)
                username = u.username
            except User.DoesNotExist:
                pass

        if username is None:
            try:
                tp = TutorProfile.objects.get(email=loginname)
                u = tp.user
                username = u.username
            except TutorProfile.DoesNotExist:
                pass

        if username is None:
            try:
                tp = TutorProfile.objects.get(studentnumber=loginname)
                u = tp.user
                username = u.username
            except TutorProfile.DoesNotExist:
                pass


        if username is None:
            return self.render_to_response(self.get_context_data(error_code='failauth'))

        password = request.POST['password']
        user = authenticate(username=username, password=password)
        try:
            tutordata = user_tutor_data(user)
        except NotTutor as e:
            try:
                tutordata = user_rus_data(user)
            except NotTutor as e:
                return self.render_to_response(self.get_context_data(error_code=e.value))
        login(request, user)
        if hasattr(tutordata, 'rus') and tutordata.rus:
            return redirect('rus_start')
        try:
            return HttpResponseRedirect(request.POST['next'])
        except KeyError:
            return redirect('news')

    def get_context_data(self, **kwargs):
        try:
            error_code = kwargs.pop('error_code')
        except KeyError:
            error_code = ''

        context_data = super(LoginView, self).get_context_data(**kwargs)

        errors = {
            'failauth': 'Forkert brugernavn eller kodeord.',
            'djangoinactive': 'Din bruger er inaktiv.',
            'notutorprofile': 'Din bruger har ingen tutorprofil.',
            'notutoryear': 'Du er ikke tutor i år.',
        }

        context_data['error'] = errors.get(error_code, '')

        return context_data

login_view = LoginView.as_view()
logout_view = LogoutView.as_view()
