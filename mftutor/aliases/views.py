from django.views.generic import TemplateView
from django.contrib.sites.shortcuts import get_current_site
from ..tutor.models import TutorGroup, Tutor
from .models import resolve_aliases_reversed

class AliasesView(TemplateView):
    template_name = 'aliases.html'

    def get_queryset(self, request):
        return TutorGroup.visible_groups.all()

    def get(self, request, **kwargs):
        current_site = get_current_site(request)
        queryset = self.get_queryset(request).distinct()
        aliases_list = resolve_aliases_reversed([g.handle for g in queryset])

        groups = []
        for g in queryset:
            if g.handle == 'alle':
                continue

            tutors = sorted(t.profile.name
                            for t in Tutor.members(request.year).filter(groups=g))
            aliases = [a + '@' + current_site.domain
                       for a in aliases_list[g.handle]]
            group = {
                'name': g.name,
                'handle': g.handle,
                'tutors': tutors,
                'aliases': aliases
            }
            groups.append(group)

        params = {
            'groups': groups,
        }
        return self.render_to_response(params)

class MyGroupsView(AliasesView):
    def get_queryset(self, request):
        return request.tutor.groups
