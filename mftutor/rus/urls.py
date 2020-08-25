from django.contrib.auth.decorators import login_required
from django.urls import path, re_path
from django.views.generic import TemplateView

from mftutor.rus.views import (
    RusNewsView, RusStartView, RusClassView, RusClassDetailView,
    RusClassDetailsPrintView, ProfileView, RusPasswordChangeView,
    TutorListView,
)

static_pages = [path(x + '/', TemplateView.as_view(template_name='rus/'+x+'.html'), name='rus_'+x) for x in (
        'gallery',
        'kontakt',
        'program',
        'kalender',
        'rusbrev',
        'rse',
        'bogliste',
        'dinData',

        )]
urlpatterns = static_pages + [
    path('', RusStartView.as_view(), name='rus_start'),
    path('profil/', ProfileView.as_view(), name='rus_profil'),
    re_path(r'^nyheder/(?:(?P<year>\d+)/(?:(?P<month>\d+)/(?:(?P<day>\d+)/(?:(?P<pk>\d+)/)?)?)?)?$', RusNewsView.as_view(), name='rus_nyheder'),
    path('holdtutorer/', login_required(TutorListView.as_view()), name='rus_holdtutorer'),
    path('holdlisterne/', RusClassView.as_view(), name='rus_holdlisterne'),
    path('holdlisterne/<handle>/', RusClassDetailView.as_view(), name='rus_holdlisterne'),
    path('holdlisterne/<handle>.tex', RusClassDetailsPrintView.as_view(), name='rus_holdlister_print'),
    path('kodeord/', login_required(RusPasswordChangeView.as_view()), name='rus_password_change'),
]
