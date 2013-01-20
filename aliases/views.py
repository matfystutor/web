
from django.shortcuts import render_to_response
from django.template import RequestContext
from tutor.models import TutorGroup
from aliases.models import Alias, resolve_alias_reversed
from mftutor import siteconfig
from django.contrib.sites.models import get_current_site

def aliases_view(request):
    current_site = get_current_site(request)
    groups = [{'name': g.name,
        'handle': g.handle,
        'tutors': g.tutor_set.filter(year__exact=siteconfig.year).distinct().select_related(),
        'aliases': [a + '@' + current_site.domain for a in resolve_alias_reversed(g.handle)],
        } for g in TutorGroup.objects.filter(tutor__year__exact=siteconfig.year, visible=True).distinct().select_related()]
    params = {'groups': groups}
    return render_to_response('aliases.html', params, RequestContext(request))
