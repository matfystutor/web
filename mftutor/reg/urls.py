from django.urls import path

from .views import ArrivedStatsView
from .views import BurStartView
from .views import ChooseSessionView, NewSessionView, EditSessionView
from .views import (
    HandoutListView, HandoutNewView, HandoutSummaryView,
    HandoutResponseView, HandoutResponseDeleteView,
    HandoutEditView,
    HandoutCrossReference,
)
from .views import LightboxAdminView
from .views import RusInfoListView, RusInfoView, RusInfoDumpView
from .views import (
    RusListView, RusCreateView, RusListRPC, RusChangesView,
    RusChangesTableView,
)
from .views import StudentnumberListView, StudentnumberView
from ..tutor.auth import tutorbur_required

urlpatterns = [
    path('', tutorbur_required(BurStartView.as_view()),
         name='bur_start'),
    path('import/', tutorbur_required(ChooseSessionView.as_view()),
         name='import_session_choose'),
    path('import/new/', tutorbur_required(NewSessionView.as_view()),
         name='import_session_new'),
    path('import/<int:pk>/', tutorbur_required(EditSessionView.as_view()),
         name='import_session_edit'),
    path('ruslist/', tutorbur_required(RusListView.as_view()),
         name='reg_rus_list'),
    path('ruslist/new/', tutorbur_required(RusCreateView.as_view()),
         name='reg_new_rus'),
    path('ruslist/rpc/', tutorbur_required(RusListRPC.as_view()),
         name='reg_rpc'),
    path('ruslist/changes/', tutorbur_required(RusChangesView.as_view()),
         name='reg_changes'),
    path('ruslist/changes/csv/', tutorbur_required(RusChangesTableView.as_view()),
         name='reg_changes_csv'),

    path('handout/', tutorbur_required(HandoutListView.as_view()),
         name='handout_list'),
    path('handout/new/', tutorbur_required(HandoutNewView.as_view()),
         name='handout_new'),
    path('handout/<int:handout>/', tutorbur_required(HandoutSummaryView.as_view()),
         name='handout_summary'),
    path('handout/<int:pk>/crossref/', tutorbur_required(HandoutCrossReference.as_view()),
         name='handout_crossref'),
    path('handout/<int:pk>/edit/', tutorbur_required(HandoutEditView.as_view()),
         name='handout_edit'),
    path('handout/<int:handout>/<rusclass>/', tutorbur_required(HandoutResponseView.as_view()),
         name='handout_response'),
    path('handout/<int:handout>/<rusclass>/delete/',
         tutorbur_required(HandoutResponseDeleteView.as_view()), name='handout_response_delete'),

    path('info/',
         RusInfoListView.as_view(), name='rusinfo_list'),
    path('info/<handle>/',
         RusInfoView.as_view(), name='rusinfo'),
    path('info/<handle>/dump/',
         RusInfoDumpView.as_view(), name='rusinfodump'),

    path('burtavle/',
         tutorbur_required(LightboxAdminView.as_view()), name='burtavle_admin'),

    path('stats/',
         ArrivedStatsView.as_view(), name='arrived_stats'),

    path('studentnumber/',
         tutorbur_required(StudentnumberListView.as_view()), name='studentnumber_list'),

    path('studentnumber/<int:pk>/',
         tutorbur_required(StudentnumberView.as_view()), name='studentnumber_set'),
]
