from django.conf.urls import patterns, url
from ..tutor.auth import tutorbur_required

from .views import BurStartView
from .views import ChooseSessionView, NewSessionView, EditSessionView
from .views import RusListView, RusCreateView, RusListRPC, RusChangesView
from .views import (
    HandoutListView, HandoutNewView, HandoutSummaryView,
    HandoutResponseView, HandoutResponseDeleteView,
    HandoutEditView,
)
from .views import RusInfoListView, RusInfoView, RusInfoDumpView
from .views import LightboxAdminView
from .views import ArrivedStatsView
from .views import StudentnumberListView, StudentnumberView

urlpatterns = patterns('',
    url(r'^$', tutorbur_required(BurStartView.as_view()),
        name='bur_start'),

    url(r'^import/$', tutorbur_required(ChooseSessionView.as_view()),
        name='import_session_choose'),
    url(r'^import/new/$', tutorbur_required(NewSessionView.as_view()),
        name='import_session_new'),
    url(r'^import/(?P<pk>\d+)/$', tutorbur_required(EditSessionView.as_view()),
        name='import_session_edit'),

    url(r'^ruslist/$', tutorbur_required(RusListView.as_view()),
        name='reg_rus_list'),
    url(r'^ruslist/new/$', tutorbur_required(RusCreateView.as_view()),
        name='reg_new_rus'),
    url(r'^ruslist/rpc/$', tutorbur_required(RusListRPC.as_view()),
        name='reg_rpc'),
    url(r'^ruslist/changes/$', tutorbur_required(RusChangesView.as_view()),
        name='reg_changes'),

    url(r'^handout/$', tutorbur_required(HandoutListView.as_view()),
        name='handout_list'),
    url(r'^handout/new/$', tutorbur_required(HandoutNewView.as_view()),
        name='handout_new'),
    url(r'^handout/(?P<handout>\d+)/$', tutorbur_required(HandoutSummaryView.as_view()),
        name='handout_summary'),
    url(r'^handout/(?P<pk>\d+)/edit/$', tutorbur_required(HandoutEditView.as_view()),
        name='handout_edit'),
    url(r'^handout/(?P<handout>\d+)/(?P<rusclass>[a-z0-9]+)/$', tutorbur_required(HandoutResponseView.as_view()),
        name='handout_response'),
    url(r'^handout/(?P<handout>\d+)/(?P<rusclass>[a-z0-9]+)/delete/$',
        tutorbur_required(HandoutResponseDeleteView.as_view()), name='handout_response_delete'),

    url(r'^info/$',
        RusInfoListView.as_view(), name='rusinfo_list'),
    url(r'^info/(?P<handle>[a-z0-9]+)/$',
        RusInfoView.as_view(), name='rusinfo'),
    url(r'^info/(?P<handle>[a-z0-9]+)/dump/$',
        RusInfoDumpView.as_view(), name='rusinfodump'),

    url(r'^burtavle/$',
        tutorbur_required(LightboxAdminView.as_view()), name='burtavle_admin'),

    url(r'^stats/$',
        ArrivedStatsView.as_view(), name='arrived_stats'),

    url(r'^studentnumber/$',
        tutorbur_required(StudentnumberListView.as_view()), name='studentnumber_list'),

    url(r'^studentnumber/(?P<pk>\d+)/$',
        tutorbur_required(StudentnumberView.as_view()), name='studentnumber_set'),
)
