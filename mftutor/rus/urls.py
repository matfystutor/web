from django.conf.urls import patterns, url
from django.views.generic import TemplateView

static_pages = [url('^'+x+'/', TemplateView.as_view(template_name='rus/'+x+'.html'), name='rus_'+x) for x in (
        'kontakt',
        'nyheder',
        'program',
        'kalender',
        'rusbrev',
        'rusbog',
        'holdlister',
        )]
urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='rus/start.html'), name='rus_start'),
    *static_pages)
