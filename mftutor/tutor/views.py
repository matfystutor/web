# encoding: utf-8

from __future__ import unicode_literals

import io
import subprocess

from django.http import HttpResponse, HttpResponseRedirect
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

from mftutor.tutor.models import TutorProfile, TutorGroup, \
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


class TutorListView(TemplateView):
    template_name = 'tutors.html'

    def get_context_data(self, **kwargs):
        context_data = super(TutorListView, self).get_context_data(**kwargs)
        group = self.kwargs.get('group')
        if group is None:
            tutors = Tutor.members(self.request.year)
            best = TutorGroup.objects.get(
                handle='best', year=self.request.year)
            leader = best.leader
        else:
            tg = get_object_or_404(
                TutorGroup, handle=group, year=self.request.year)
            tutors = Tutor.group_members(tg)
            leader = tg.leader

        leader_pk = leader.pk if leader else 0

        def make_tutor_dict(t):
            return {
                'pk': t.pk,
                'studentnumber': t.profile.studentnumber,
                'picture': t.profile.picture.url if t.profile.picture else '',
                'full_name': t.profile.get_full_name(),
                'street': t.profile.street,
                'city': t.profile.city,
                'phone': t.profile.phone,
                'email': t.profile.email,
                'study': t.profile.study,
            }

        tutors = [make_tutor_dict(t) for t in tutors]
        if group == 'tutorsmiley' and self.request.year in [2015]:
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

        context_data['group'] = group
        context_data['tutor_list'] = tutors
        context_data['groups'] = groups
        context_data['tutor_count'] = len(tutors)
        context_data['leader_pk'] = leader_pk
        if leader_pk:
            try:
                context_data['leader'] = next(
                    t for t in tutors
                    if t['pk'] == leader_pk
                )
            except StopIteration:
                # leader is not in tutors
                context_data['leader'] = make_tutor_dict(
                    Tutor.objects.get(pk=leader_pk))
        return context_data


tutors_view = TutorListView.as_view()


class TutorDumpView(TutorListView):
    template_name = 'contacts.csv'

    def get_context_data(self, **kwargs):
        context_data = super(TutorDumpView, self).get_context_data(**kwargs)
        context_data['person_list'] = [
            {
                'name': p['full_name'],
                'email': p['email'],
                'phone': p['phone'],
            }
            for p in context_data['tutor_list']
        ]
        return context_data

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = 'text/csv'
        return super(TutorDumpView, self).render_to_response(
            context, **response_kwargs)


class TutorDumpLDIFView(TutorDumpView):
    def get(self, request, *args, **kwargs):
        context_data = self.get_context_data(**kwargs)

        try:
            import ldif3
        except ImportError:
            s = 'No ldif3 module\n'
            return HttpResponse(s, content_type='text/plain; charset=utf8')

        buf = io.BytesIO()
        ldif_writer = ldif3.LDIFWriter(buf)
        person_list = context_data['person_list']
        for person in person_list:
            dn = 'cn=%s' % person['name']
            entry = {
                'cn': [person['name']],
                'mail': [person['email']],
                'phone': [person['phone']],
            }
            ldif_writer.unparse(dn, entry)

        return HttpResponse(
            buf.getvalue(),
            content_type='text/plain; charset=utf8')


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
    update_leader_group = forms.BooleanField(
        required=False, label="Opdater gruppeansvarlig-gruppen")

    def __init__(self, year, groups, *args, **kwargs):
        super(GroupLeaderForm, self).__init__(*args, **kwargs)
        self.tutor_year = year

        for i, group_dict in enumerate(groups):
            group = TutorGroup.objects.get(pk=group_dict["pk"])

            tutors = list(Tutor.members(year).filter(groups=group))
            choices = [
                (tu.pk, tu.profile.name)
                for tu in tutors
            ]
            if group.leader and group.leader not in tutors:
                name = '%s (ej medlem)' % group.leader.profile.name
                choices.append((group.leader.pk, name))
            choices[0:0] = [('', '')]

            current_leader = group.leader.pk if group.leader else ''

            self.fields['group_%s' % group.pk] = forms.ChoiceField(
                label=group.name,
                required=False,
                choices=choices,
                initial=current_leader)


class GroupLeaderViewBase(FormView):
    form_class = GroupLeaderForm
    template_name = 'groupleaderadmin.html'

    def get_form_kwargs(self):
        kwargs = super(GroupLeaderViewBase, self).get_form_kwargs()
        kwargs['year'] = self.request.year
        kwargs['groups'] = self.get_groups()
        return kwargs

    def form_valid(self, form):
        groups = self.get_groups()
        changes = []
        for group in groups:
            new_leader_pk = form.cleaned_data['group_%s' % group['pk']]
            new_leader = int(new_leader_pk) if new_leader_pk else None
            if group['leader'] != new_leader:
                changes.append((group, new_leader))
        self.change_leaders(changes)

        return self.render_to_response(
            self.get_context_data(form=form, success=True))

    def get_groups(self):
        raise NotImplementedError

    def change_leaders(self, changes):
        raise NotImplementedError


class GroupLeaderView(GroupLeaderViewBase):
    form_class = GroupLeaderForm
    template_name = 'groupleaderadmin.html'

    def get_groups(self):
        qs = TutorGroup.objects.filter(
            visible=True, year=self.request.year)
        qs = qs.prefetch_related('tutor_set__profile')
        groups = []
        for g in qs:
            tutor_qs = g.tutor_set.all()
            tutors = [(tu.pk, tu.profile.name) for tu in tutor_qs]
            groups.append({
                'pk': g.pk,
                'name': g.name,
                'tutors': tutors,
                'leader': g.leader_id,
            })
        return groups

    # Only called if leader group exists in form_valid, so no try/catch is ok
    def change_leaders(self, changes):
        for group, new_leader in changes:
            gr = TutorGroup.objects.get(pk=group['pk'])
            gr.leader_id = new_leader or None
            gr.save()

        # additionally, update leader_group
        leader_group = TutorGroup.objects.get(
            handle='gruppeansvarlige', year=self.request.year)

        group_leader_tuple_index = 1
        leader_group.tutor_set = [change[group_leader_tuple_index] for change in changes]

    def form_valid(self, form):
        # Make sure group named 'grouppeansvarlige' exists
        # because we add every grouppeansvarlig to that group
        if form.cleaned_data['update_leader_group']:
            try:
                leader_group = TutorGroup.objects.get(
                    handle='gruppeansvarlige', year=self.request.year)
            except TutorGroup.DoesNotExist:
                form.add_error(
                    'update_leader_group',
                    'Ingen gruppe hedder "gruppeansvarlige"')
                return self.form_invalid(form)

        return super(GroupLeaderView, self).form_valid(form)


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
