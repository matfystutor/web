# encoding: utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect, render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.contrib.auth.views import password_change
from django.views.generic import ListView, UpdateView, TemplateView
from ..settings import YEAR
from .models import *
from .viewimpl.loginout import logout_view, login_view
from .viewimpl.profile import profile_view
from .viewimpl.admin import TutorAdminView
from .auth import tutor_required, user_tutor_data

def tutor_password_change_view(request):
    if 'back' in request.GET:
        back = request.GET['back']
    else:
        back = reverse('news')
    return password_change(request, 'registration/password_change_form.html', back)

class UploadPictureForm(forms.ModelForm):
    picture = forms.FileField(
            required=True,
            label='Billede')

    class Meta:
        model = TutorProfile
        fields = ('picture',)

class UploadPictureView(UpdateView):
    model = TutorProfile
    template_name = 'uploadpicture.html'
    form_class = UploadPictureForm
    def get_object(self):
        return self.request.user.get_profile()
    def get_success_url(self):
        return reverse('upload_picture_view')

def tutors_view(request, group=None):
    lookup_group = group or 'alle'

    tutorgroup = get_object_or_404(TutorGroup, handle=lookup_group)

    leader = tutor_group_leader(lookup_group, YEAR)
    leader_pk = leader.pk if leader else -1

    tutors = list(Tutor.members.group(lookup_group))
    tutors = [{
        'pk': t.pk,
        'studentnumber': t.profile.studentnumber,
        'picture': t.profile.picture.url if t.profile.picture else '',
        'full_name': t.profile.get_full_name(),
        'street': t.profile.street,
        'city': t.profile.city,
        'phone': t.profile.phone,
        'email': t.profile.user.email if t.profile.user else '',
        'study': t.profile.study,
        } for t in tutors]
    tutors.sort(key=lambda t: (t['pk'] != leader_pk, t['full_name']))

    groups = TutorGroup.visible_groups.all()

    return render_to_response('tutors.html',
            {
                'group': group,
                'tutor_list': tutors,
                'groups': groups,
                },
            RequestContext(request))

def switch_user(request, new_user):
    from django.contrib.auth import authenticate, login
    user = authenticate(username=new_user, current_user=request.user)
    if user is not None:
        login(request, user)
    return HttpResponseRedirect(reverse('news'))

class FrontView(TemplateView):
    template_name = 'front.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('news'))

        return super(FrontView, self).get(request, *args, **kwargs)
