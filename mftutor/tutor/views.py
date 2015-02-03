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
from .viewimpl.admin import TutorAdminView, BoardAdminView
from .auth import tutor_required, user_tutor_data, user_rus_data, NotTutor

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
        'email': t.profile.email,
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
        try:
            d = user_tutor_data(request.user)
            return HttpResponseRedirect(reverse('news'))
        except NotTutor:
            pass

        try:
            d = user_rus_data(request.user)
            return HttpResponseRedirect(reverse('rus_start'))
        except NotTutor:
            pass

        return super(FrontView, self).get(request, *args, **kwargs)


class GroupLeaderForm(forms.Form):
    def __init__(self, year, groups):
        super(GroupLeaderForm, self).__init__()
        self.tutor_year = year

        for i, group in enumerate(groups):
            choices = [
                (tu.pk, tu.profile.name)
                for tu in Tutor.objects.filter(year=year, groups=group)
            ]

            try:
                current_leader = TutorGroupLeader.objects.get(
                    year=year, group=group).tutor.pk
            except TutorGroupLeader.DoesNotExist:
                current_leader = ''

            self.fields['group_%s' % group.handle] = forms.ChoiceField(
                required=False,
                choices=choices,
                initial=current_leader)


class GroupLeaderView(FormView):
    form_class = GroupLeaderForm
    template_name = 'groupleaderadmin.html'

    def form_valid(self, form):
        for field in form:
            if not field.name.startswith('group_'):
                continue

            handle = field.name[6:]

            try:
                current_leader = TutorGroupLeader.objects.get(
                    year=year, group=group)
            except TutorGroupLeader.DoesNotExist:
                current_leader = TutorGroupLeader(
                    year=year, group=group)

            if field.data:
                new_leader = Tutor.objects.get(pk=field.data)
            else:
                new_leader = None

            if current_leader.tutor != new_leader:
                current_leader.tutor = new_leader
                current_leader.save()
