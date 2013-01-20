# encoding: utf-8
from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.core.urlresolvers import NoReverseMatch
from django.contrib.auth.models import User
from tutor.models import TutorProfile
from tutor.auth import user_tutor_data, NotTutor
def logout_view(request):
    logout(request)
    try:
        return redirect(request.GET['next'])
    except NoReverseMatch:
        pass
    return redirect('news')

def login_view(request, err=''):
    if request.method == 'POST':
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
                u = User.objects.get(email=loginname)
                username = u.username
            except User.DoesNotExist:
                pass

        if username is None:
            try:
                tp = TutorProfile.objects.get(studentnumber=loginname)
                u = tp.user
                username = u.username
            except TutorProfile.DoesNotExist:
                pass

        if username is None:
            return redirect('login_error', err='failauth')

        password = request.POST['password']
        user = authenticate(username=username, password=password)
        try:
            tutordata = user_tutor_data(user)
        except NotTutor as e:
            return redirect('login_error', err=e.value)
        login(request, user)
        try:
            return redirect(request.POST['next'])
        except NoReverseMatch:
            pass
        return redirect('news')
    else:
        errormessage = ''
        if 'err' in request.GET:
            err = request.GET['err']
            if err == 'failauth':
                errormessage = 'Forkert brugernavn eller kodeord.'
            elif err == 'djangoinactive':
                errormessage = 'Din bruger er inaktiv.'
            elif err == 'notutorprofile':
                errormessage = 'Din bruger har ingen tutorprofil.'
            elif err == 'notutoryear':
                errormessage = 'Du er ikke tutor i år.'
        return render(request, 'login_form.html', {'error': errormessage})
