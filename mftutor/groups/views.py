from django.views.generic import TemplateView
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from ..tutor.models import TutorGroup, Tutor
from ..aliases.models import resolve_alias_reversed

class GroupsView(TemplateView):
    template_name = 'groups/groups.html'

    def get_queryset(self, request):
        return TutorGroup.visible_groups.all()

    def get(self, request, **kwargs):
        current_site = get_current_site(request)
        queryset = self.get_queryset(request).distinct()

        groups = []
        for g in queryset:
            if g.handle == 'alle':
                continue

            leader = g.leader
            size = sum(1 for t in Tutor.members(request.year).filter(groups=g))
            group = {
                'name': g.name,
                'leader': leader,
                'handle': g.handle,
                'size': size
            }
            groups.append(group)

        params = {
            'groups': groups,
        }
        return self.render_to_response(params)

class MyGroupsView(GroupsView):
    def get_queryset(self, request):
        return request.tutor.groups

class GroupView(TemplateView):
    template_name = 'groups/group.html'

    def get_context_data(self, **kwargs):
        context_data = super(GroupView, self).get_context_data(**kwargs)
        group = self.kwargs.get('group') # grouphandle
        
        aliases = [a + '@' + get_current_site("").domain for a in resolve_alias_reversed(group)] # TODO: fix empty request
        
        if group is None:
            #Could this even happen?
            tutors = Tutor.members(self.request.year)
            best = TutorGroup.objects.get(
                handle='best', year=self.request.year)
            leader = best.leader
            group_name = "Tutorer"
        else:
            tg = get_object_or_404(
                TutorGroup, handle=group, year=self.request.year)
            tutors = Tutor.group_members(tg)
            leader = tg.leader
            group_name = tg.name

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
            }

        tutors = [make_tutor_dict(t) for t in tutors]
        tutors.sort(key=lambda t: (t['pk'] != leader_pk, t['full_name']))

        context_data['group'] = group
        context_data['group_name'] = group_name        
        context_data['tutor_list'] = tutors
        context_data['tutor_count'] = len(tutors)
        context_data['leader_pk'] = leader_pk
        context_data['aliases'] = aliases
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
