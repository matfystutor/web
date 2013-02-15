from django.views.generic import TemplateView
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from tutor.models import TutorGroup, TutorProfile
from activation.models import ProfileActivation
from aliases.models import Alias, resolve_alias_reversed
from mftutor.settings import YEAR
from django.contrib.sites.models import get_current_site
from tutor.auth import user_tutor_data

class AliasesView(TemplateView):
    template_name = 'aliases.html'

    def filter_queryset(self, request, queryset):
        return queryset.filter(visible=True)

    def get(self, request):
        current_site = get_current_site(request)
        queryset = TutorGroup.objects.filter(tutor__year__exact=YEAR)
        queryset = self.filter_queryset(request, queryset).distinct()
        aliases_list = resolve_alias_reversed([g.handle for g in queryset])

        groups = [{'name': g.name,
            'handle': g.handle,
            'tutors': g.tutor_set.filter(year__exact=YEAR).distinct().select_related(),
            'aliases': [a + '@' + current_site.domain for a in aliases_list[g.handle]],
            } for g in queryset]
        params = {'groups': groups}
        return self.render_to_response(params)

class MyGroupsView(AliasesView):
    def filter_queryset(self, request, queryset):
        utd = user_tutor_data(request.user)
        return queryset.filter(tutor__profile=utd.profile)
