from django.views.generic import TemplateView
from django.shortcuts import render_to_response
from django.template import RequestContext
from tutor.models import TutorGroup
from aliases.models import Alias, resolve_alias_reversed
from mftutor.settings import YEAR
from django.contrib.sites.models import get_current_site

class AliasesView(TemplateView):
    template_name = 'aliases.html'

    def get(self, request):
        current_site = get_current_site(request)
        groups = [{'name': g.name,
            'handle': g.handle,
            'tutors': g.tutor_set.filter(year__exact=YEAR).distinct().select_related(),
            'aliases': [a + '@' + current_site.domain for a in resolve_alias_reversed(g.handle)],
            } for g in TutorGroup.objects.filter(tutor__year__exact=YEAR, visible=True).distinct().select_related()]
        params = {'groups': groups}
        return self.render_to_response(params)
