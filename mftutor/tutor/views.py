import io
import subprocess
import tempfile

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.template import Context
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from django import forms
from django.views.generic import TemplateView, FormView, ListView
from fpdf import FPDF

from mftutor.tutor.models import TutorProfile, TutorGroup, \
    Tutor, BoardMember

# Reexport the following views:
from mftutor.tutor.viewimpl.loginout import logout_view, login_view
from mftutor.tutor.viewimpl.profile import profile_view
from mftutor.tutor.viewimpl.admin import TutorAdminView, BoardAdminView


# def tutor_password_change_view(request):
#     if 'back' in request.GET:
#         back = request.GET['back']
#     else:
#         back = reverse('news')
#     return password_change(
#         request, 'registration/password_change_form.html', back)


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
                'picture': t.profile.picture,
                'full_name': t.profile.get_full_name(),
                'street': t.profile.street,
                'city': t.profile.city,
                'phone': t.profile.phone,
                'email': t.profile.email,
                'study': t.profile.study,
                'nickname': t.profile.nickname,
            }

        tutors = [make_tutor_dict(t) for t in tutors]
        if group == 'tutorsmiley' and self.request.year in [2015]:
            tutors.append({
                'pk': ':)',
                'studentnumber': '88888888',
                'picture': None,
                'full_name': 'Smiley',
                'street': 'Skovbrynet 5',
                'city': 'Smilets By',
                'phone': '88888888',
                'email': 'SMILEY@SMILEY.☺',
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
                'nickname': p['nickname'],
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
        debug = {'current': [group['leader'] for group in groups],
                 'new': [form.cleaned_data['group_%s' % group['pk']] for group in groups]}
        for group in groups:
            new_leader_pk = form.cleaned_data['group_%s' % group['pk']]
            new_leader = int(new_leader_pk) if new_leader_pk else None
            if group['leader'] != new_leader:
                changes.append((group, new_leader))
        debug['changes'] = changes
        self.change_leaders(changes)

        return self.render_to_response(
            self.get_context_data(form=form, success=True, changes=repr(debug)))

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
                raise ValidationError('Ukendt årskortnummer %r' % (sn,))
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
            sender = '"Mat/Fys-Tutorgruppen" <webfar@matfystutor.dk>'
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
                        webfar='Thomas Skovlund Hansen'
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


class KrydslisteCreateForm(forms.Form):
    value = forms.CharField(label='input')
    check_rtd = forms.BooleanField(initial=False, required=False, label='check_rtd')


class KrydslisteView(FormView):
    template_name = 'krydsliste.html'
    form_class = KrydslisteCreateForm

    def form_valid(self, form):
        KrydslisteCreateForm.check_rtd = form.cleaned_data['check_rtd']
        pdf = PDF(orientation='P', unit='mm', format='A3', rtd=KrydslisteCreateForm.check_rtd)
        pdf.create(form.cleaned_data['value'].splitlines())
        with tempfile.NamedTemporaryFile() as f:
            res = pdf.output(f.name, 'F')
            return HttpResponse(f.read(), content_type='application/pdf')


class PDF(FPDF):
    w, h = 297, 420
    header_font_size = 60
    name_font_size = 24
    line_width_l = 2
    line_width_s = 0
    box_height = 15
    names_pr_page = int(round((h - 2 * box_height) / box_height))
    max_name_length = 20

    def __init__(self, *args, rtd=None, **kwargs):
        super(PDF, self).__init__(*args, **kwargs)

        self.fields = [
            {
                'name': 'Navn',
                'amount': 20,
                'draw_squares': False
            }, {
                'name': 'Øl',
                'amount': 30,
                'draw_squares': True
            }, {
                'name': 'Vand',
                'amount': 20,
                'draw_squares': True
            }, {
                'name': 'GD',
                'amount': 20,
                'draw_squares': True
            },
        ]

        if rtd:
            self.fields.append({
                'name': 'RTD',
                'amount': 20,
                'draw_squares': True
            })

    cell_width = 0

    # Draw the cross list header ( uses the data of fields for easy manipulation)
    def create_header(self):
        self.set_line_width(self.line_width_l)

        # Create the header line
        header_line_height = 2 * self.box_height
        self.line(0, header_line_height, self.w, header_line_height)

        # Draw the horizontal lines and write the headers
        current_pos = 0
        for f in self.fields:
            self.set_line_width(self.line_width_s)
            small_squares = f.get("amount")
            # Draw lines in between fields if draw_square is set
            if f.get("draw_squares"):
                for i in range(small_squares):
                    current_pos += 1
                    self.line(current_pos * self.cell_width, header_line_height, current_pos * self.cell_width,
                              self.h)
            else:
                current_pos = current_pos + small_squares

            # Draw the thick line at the end of the field
            self.set_line_width(self.line_width_l)
            w = current_pos * self.cell_width
            self.line(w, 0, w, self.h)

            # Write in the text
            self.set_xy((current_pos - small_squares) * self.cell_width, 0)
            self.set_font('Arial', "", self.header_font_size)
            self.set_text_color(0, 0, 0)
            self.multi_cell(w=self.cell_width * small_squares, h=header_line_height, align='C', txt=f.get('name'))

    # Create the cross list this method creates all the pages and populates the data
    def create(self, names):
        # Calculate missing cells to fill out the entire page
        total_cells = 0
        for f in self.fields:
            total_cells += f.get("amount")

        self.cell_width = self.w / total_cells

        missing_names = int(round(self.names_pr_page - (len(names) % self.names_pr_page)))

        for i in range(missing_names):
            names.append("")

        first_field_size = self.fields[0].get("amount")
        # Insert all the names and create new pages when one is filled out
        for index in range(len(names)):
            if index % self.names_pr_page == 0:
                self.add_page()
                self.create_header()
            self.draw_name_box(index, names[index], first_field_size)

    # Draw the name box at the given index
    def draw_name_box(self, index, name, field_size):
        height_y = ((index % self.names_pr_page) + 3) * self.box_height

        self.set_line_width(self.line_width_l)
        self.line(0, height_y, self.w, height_y)

        self.set_line_width(self.line_width_s)
        self.line(field_size * self.cell_width, height_y - self.box_height / 2, self.w,
                  height_y - self.box_height / 2)

        self.set_font_size(self.name_font_size)
        self.text(x=1, y=height_y - 5, txt=self.minify_name(name))

    def minify_name(self, name):
        name_split = str.split(name, ' ')
        for i in range(1, len(name_split) - 1):
            name_split[i] = name_split[i][0] + "."
        return ' '.join(name_split)[0:self.max_name_length]


if __name__ == '__main__':
    names = [
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
        'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
        'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'Æ',
        'Ø', 'Å', 'A B C',
    ]
    pdf = PDF(orientation='P', unit='mm', format='A3', rtd=False)
    pdf.create(names)
    pdf.output('test.pdf', 'F')
