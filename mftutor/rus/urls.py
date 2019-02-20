from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from mftutor.rus.views import (
    RusNewsView, RusStartView, RusClassView, RusClassDetailView,
    RusClassDetailsPrintView, ProfileView, RusPasswordChangeView,
    TutorListView,
)

static_pages = [url('^'+x+'/', TemplateView.as_view(template_name='rus/'+x+'.html'), name='rus_'+x) for x in (
        'gallery',
        'kontakt',
        'program',
        'kalender',
        'rusbrev',
        'rse',
        'bogliste',
        )]
urlpatterns = static_pages + [
    url(r'^$', RusStartView.as_view(), name='rus_start'),
    url(r'^profil/$', ProfileView.as_view(), name='rus_profil'),
    url(r'^nyheder/(?:(?P<year>\d+)/(?:(?P<month>\d+)/(?:(?P<day>\d+)/(?:(?P<pk>\d+)/)?)?)?)?$', RusNewsView.as_view(), name='rus_nyheder'),
    url(r'^holdtutorer/$', login_required(TutorListView.as_view()), name='rus_holdtutorer'),
    url(r'^holdlister/$', RusClassView.as_view(), name='rus_holdlister'),
    url(r'^holdlister/(?P<handle>[a-z0-9]+)/$', RusClassDetailView.as_view(), name='rus_holdlister'),
    url(r'^holdlister/(?P<handle>[a-z0-9]+)\.tex$', RusClassDetailsPrintView.as_view(), name='rus_holdlister_print'),
    url(r'^kodeord/$', login_required(RusPasswordChangeView.as_view()), name='rus_password_change'),
]
