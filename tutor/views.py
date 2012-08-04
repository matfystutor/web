# encoding: utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.core.urlresolvers import reverse, NoReverseMatch
from django.template import RequestContext
from tutor.models import Tutor, TutorProfile, user_tutor_data
from django.contrib.auth import logout, authenticate, login

def logout_view(request):
    logout(request)
    try:
        return redirect(request.GET['next'])
    except NoReverseMatch:
        pass
    return redirect('news')

def login_view(request, err=''):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        tutordata = user_tutor_data(user)
        if tutordata['err'] is not None:
            return redirect('login_error', err=tutordata['err'])
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
