from django.contrib.auth.views import PasswordChangeView
from django.urls import path, reverse_lazy, include

from .auth import tutorbest_required, tutor_required
from .views import (
    logout_view, login_view, profile_view,
    tutors_view, TutorAdminView, FrontView,
    BoardAdminView, GroupLeaderView, ResetPasswordView, BoardMemberListView,
    TutorDumpView, TutorDumpLDIFView)
from ..aliases.views import MyGroupsView

urlpatterns = [
    path('', FrontView.as_view(), name='front'),
    path('tutors/', tutor_required(tutors_view), name='tutors'),
    path('tutors/<group>/', tutor_required(tutors_view), name='tutorgroup'),
    path('tutordump/', tutor_required(TutorDumpView.as_view()), name='tutordump'),
    path('tutordump/<group>/', tutor_required(TutorDumpView.as_view()), name='tutordumpgroup'),
    path('tutordumpldif/', tutor_required(TutorDumpLDIFView.as_view()), name='tutordumpldif'),
    path('tutordumpldif/<group>/', tutor_required(TutorDumpLDIFView.as_view()), name='tutordumpgroupldif'),
    path('board/', BoardMemberListView.as_view(), name='board'),
    path('logout/', logout_view, name="logout_view"),
    path('login/', login_view, name='tutor_login'),
    path('login/?err=<err>', login_view, name='login_error'),
    path('profile/', tutor_required(profile_view), name='profile_view'),
    path('profile/password/',
         tutor_required(PasswordChangeView.as_view(success_url=reverse_lazy('front'))),
         name='password_change'
         ),
    path('aliases/me/', tutor_required(MyGroupsView.as_view()), name='groups_view'),
    path('tutoradmin/', tutorbest_required(TutorAdminView.as_view()), name='tutor_admin'),
    path('gruppeansvarlige/', tutorbest_required(GroupLeaderView.as_view()), name='groupleader_admin'),
    path('resetpassword/', tutorbest_required(ResetPasswordView.as_view()), name='reset_password'),
    path('boardadmin/<int:year>/', tutorbest_required(BoardAdminView.as_view()), name='board_admin'),
    path('su/', include('django_su.urls')),
]
