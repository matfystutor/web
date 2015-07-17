# encoding: utf-8

from __future__ import unicode_literals

import subprocess

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.template import RequestContext
from django.template import Context
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from django import forms
from django.contrib.auth.views import password_change
from django.views.generic import UpdateView, TemplateView, FormView, ListView

from mftutor.tutor.models import TutorProfile, TutorGroup, TutorGroupLeader, \
    Tutor, BoardMember

# Reexport the following views:
from mftutor.tutor.viewimpl.loginout import logout_view, login_view
from mftutor.tutor.viewimpl.profile import profile_view
from mftutor.tutor.viewimpl.admin import TutorAdminView, BoardAdminView


def tutor_password_change_view(request):
    if 'back' in request.GET:
        back = request.GET['back']
    else:
        back = reverse('news')
    return password_change(
        request, 'registration/password_change_form.html', back)


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
        return self.request.user.tutorprofile

    def get_success_url(self):
        return reverse('upload_picture_view')


def tutors_view(request, group=None):
    if group is None:
        tutors = Tutor.members(request.year)
        try:
            leader = TutorGroupLeader.objects.get(
                group__handle='best', year=request.year).tutor
        except TutorGroupLeader.DoesNotExist:
            leader = None
    else:
        tg = get_object_or_404(TutorGroup, handle=group, year=request.year)
        tutors = Tutor.group_members(tg)

        try:
            leader = TutorGroupLeader.objects.get(
                group__handle=group, year=request.year).tutor
        except TutorGroupLeader.DoesNotExist:
            leader = None

    leader_pk = leader.pk if leader else -1

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
    if group == 'tutorsmiley' and request.year in [2015]:
        tutors.append({
            'pk': ':)',
            'studentnumber': '88888888',
            'picture': '/upload/tutorpics/smiley.png',
            'full_name': 'Smiley',
            'street': 'Skovbrynet 5',
            'city': 'Smilets By',
            'phone': '88888888',
            'email': u'SMILEY@SMILEY.☺',
            'study': 'Smil',
        })
    tutors.sort(key=lambda t: (t['pk'] != leader_pk, t['full_name']))

    groups = TutorGroup.visible_groups.all()

    return render_to_response(
        'tutors.html',
        {
            'group': group,
            'tutor_list': tutors,
            'groups': groups,
            'tutor_count': len(tutors),
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
        if request.tutor:
            return HttpResponseRedirect(reverse('news'))
        elif request.rus:
            return HttpResponseRedirect(reverse('rus_start'))
        else:
            return super(FrontView, self).get(request, *args, **kwargs)


class GroupLeaderForm(forms.Form):
    def __init__(self, year, groups, *args, **kwargs):
        super(GroupLeaderForm, self).__init__(*args, **kwargs)
        self.tutor_year = year

        for i, group in enumerate(groups):
            choices = [
                (tu.pk, tu.profile.name)
                for tu in Tutor.objects.filter(year=year, groups=group)
            ]
            choices[0:0] = [('', '')]

            try:
                current_leader = TutorGroupLeader.objects.get(
                    year=year, group=group).tutor.pk
            except TutorGroupLeader.DoesNotExist:
                current_leader = ''

            self.fields['group_%s' % group.pk] = forms.ChoiceField(
                label=group.name,
                required=False,
                choices=choices,
                initial=current_leader)


class GroupLeaderView(FormView):
    form_class = GroupLeaderForm
    template_name = 'groupleaderadmin.html'

    def get_form_kwargs(self):
        kwargs = super(GroupLeaderView, self).get_form_kwargs()
        kwargs['year'] = self.request.year
        kwargs['groups'] = TutorGroup.objects.filter(
            visible=True, year=self.request.year)
        return kwargs

    def form_valid(self, form):
        for field in form:
            if not field.name.startswith('group_'):
                continue

            pk = field.name[6:]

            try:
                current_leader_object = TutorGroupLeader.objects.get(
                    year=self.request.year, group__pk=pk)
            except TutorGroupLeader.DoesNotExist:
                current_leader_object = TutorGroupLeader(
                    year=self.request.year,
                    group=TutorGroup.objects.get(pk=pk))

            try:
                current_leader = current_leader_object.tutor
            except Tutor.DoesNotExist:
                current_leader = None

            if field.data:
                new_leader = Tutor.objects.get(pk=field.data)
            else:
                new_leader = None

            if current_leader != new_leader:
                current_leader_object.tutor = new_leader
                current_leader_object.save()

        return self.render_to_response(
            self.get_context_data(form=form, success=True))


class ResetPasswordForm(forms.Form):
    studentnumbers = forms.CharField(widget=forms.Textarea)
    # confirm = forms.BooleanField(required=False)

    def clean_studentnumbers(self):
        studentnumbers = self.cleaned_data['studentnumbers']
        tps = list(
            TutorProfile.objects.filter(
                studentnumber__in=studentnumbers.split()))
        tp = dict((tp.studentnumber, tp) for tp in tps)
        for sn in studentnumbers.split():
            if sn not in tp:
                raise ValidationError(u'Ukendt årskortnummer %r' % (sn,))
        return tps


def generate_passwords(pw_length, num_pw):
    p = subprocess.Popen(
        ('pwgen',
         '--capitalize',
         '--numerals',
         str(pw_length),
         str(num_pw)),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        universal_newlines=True)
    p.stdin.close()
    passwords = p.stdout.read().split()
    p.stdout.close()
    p.wait()
    return passwords


class ResetPasswordView(FormView):
    template_name = 'reset_password.html'
    form_class = ResetPasswordForm

    def form_valid(self, form):
        data = form.cleaned_data
        if 'confirm' in self.request.POST:
            subject = 'Nyt kodeord til tutorhjemmesiden'
            sender = '"Mathias Rav" <webfar@matfystutor.dk>'
            body = get_template('emails/new_password.txt')

            tps = data['studentnumbers']
            passwords = generate_passwords(8, len(tps))
            messages = []
            for tp, password in zip(tps, passwords):
                messages.append(EmailMessage(
                    subject=subject,
                    from_email=sender,
                    body=body.render(Context(dict(
                        navn=tp.name,
                        username=tp.studentnumber,
                        password=password,
                        webfar='Mathias Rav'
                    ))),
                    to=['"%s" <%s>' % (tp.name, tp.email)],
                ))
                tp.user.set_password(password)
                tp.user.save()

            email_backend_type = 'django.core.mail.backends.smtp.EmailBackend'

            email_backend = get_connection(backend=email_backend_type)
            email_backend.send_messages(messages)

            return self.render_to_response(
                self.get_context_data(form=form, success=True))

        else:
            return self.render_to_response(
                self.get_context_data(
                    form=form, confirm=True, tutors=data['studentnumbers']))


class BoardMemberListView(ListView):
    template_name = "board.html"
    context_object_name = "tutor_list"

    def get_queryset(self):
        qs = BoardMember.objects.filter(tutor__year=self.request.year)
        return qs.select_related()
