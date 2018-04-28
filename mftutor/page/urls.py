from django.conf.urls import patterns, url
from django.views.generic import TemplateView

static_pages = [url('^'+x+'/', TemplateView.as_view(template_name=x+'.html'), name=x) for x in (
        'vedtaegter',
        'gruppekatalog',
        'rus2tur',
        'sponsor',
        'kontakt',
        'todo',
        'intro',
        'feeds',
        )]
urlpatterns = patterns('',
    *static_pages)
