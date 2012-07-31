from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from tutor.models import Tutor
from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('tutors'))
