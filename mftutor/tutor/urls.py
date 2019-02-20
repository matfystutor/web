from django.conf.urls import url

from .auth import tutorbest_required, tutor_required
from .views import (
    logout_view, login_view, profile_view, tutor_password_change_view,
    tutors_view, TutorAdminView, switch_user, FrontView,
    BoardAdminView, GroupLeaderView, ResetPasswordView, BoardMemberListView,
    TutorDumpView, TutorDumpLDIFView)
from ..aliases.views import MyGroupsView

urlpatterns = [
    url(r'^$', FrontView.as_view(), name='front'),
    url(r'^tutors/$', tutor_required(tutors_view), name='tutors'),
    url(r'^tutors/(?P<group>[^/?]+)/$', tutor_required(tutors_view), name='tutorgroup'),
    url(r'^tutordump/$', tutor_required(TutorDumpView.as_view()), name='tutordump'),
    url(r'^tutordump/(?P<group>[^/?]+)/$', tutor_required(TutorDumpView.as_view()), name='tutordumpgroup'),
    url(r'^tutordumpldif/$', tutor_required(TutorDumpLDIFView.as_view()), name='tutordumpldif'),
    url(r'^tutordumpldif/(?P<group>[^/?]+)/$', tutor_required(TutorDumpLDIFView.as_view()), name='tutordumpgroupldif'),
    url(r'^board/$', BoardMemberListView.as_view(), name='board'),
    url(r'^logout/$', logout_view, name="logout_view"),
    url(r'^login/$', login_view, name='tutor_login'),
    url(r'^login/\?err=(?P<err>.*)$', login_view, name='login_error'),
    url(r'^profile/$', tutor_required(profile_view), name='profile_view'),
    url(r'^profile/password/$', tutor_required(tutor_password_change_view), name='password_change'),
    url(r'^aliases/me/$', tutor_required(MyGroupsView.as_view()), name='groups_view'),
    url(r'^tutoradmin/$', tutorbest_required(TutorAdminView.as_view()), name='tutor_admin'),
    url(r'^gruppeansvarlige/$', tutorbest_required(GroupLeaderView.as_view()), name='groupleader_admin'),
    url(r'^resetpassword/$', tutorbest_required(ResetPasswordView.as_view()), name='reset_password'),
    url(r'^boardadmin/(?P<year>\d+)/$', tutorbest_required(BoardAdminView.as_view()), name='board_admin'),
    url(r'^su/(?P<new_user>[^/]*)/$', switch_user),
]
