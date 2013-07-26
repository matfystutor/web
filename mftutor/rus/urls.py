from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from .views import RusNewsView, RusStartView

static_pages = [url('^'+x+'/', TemplateView.as_view(template_name='rus/'+x+'.html'), name='rus_'+x) for x in (
        'kontakt',
        'program',
        'kalender',
        'rusbrev',
        'rusbog',
        'holdlister',
        )]
urlpatterns = patterns('',
    url(r'^$', RusStartView.as_view(), name='rus_start'),
    url(r'^nyheder/(?:(?P<year>\d+)/(?:(?P<month>\d+)/(?:(?P<day>\d+)/(?:(?P<pk>\d+)/)?)?)?)?$', RusNewsView.as_view(), name='rus_nyheder'),
    *static_pages)
