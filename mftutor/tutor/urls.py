from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
from django.contrib.auth.decorators import login_required
from ..settings import YEAR
from ..aliases.views import AliasesView, MyGroupsView
from .models import Tutor, TutorGroup, BoardMember
from .views import logout_view, login_view, profile_view, tutor_password_change_view, UploadPictureView, tutors_view, TutorAdminView, switch_user, FrontView
from .auth import tutorbest_required

urlpatterns = patterns('',
    url(r'^$', FrontView.as_view(), name='front'),
    url(r'^tutors/$', login_required(tutors_view), name='tutors'),
    url(r'^tutors/([^/?]+)/$', login_required(tutors_view), name='tutorgroup'),
    url(r'^board/$',
        ListView.as_view(
            queryset=BoardMember.objects.filter(tutor__year=YEAR).select_related(),
            template_name="board.html",
            context_object_name="tutor_list"),
        name='board'),
    url(r'^logout/$', logout_view),
    url(r'^login/$', login_view),
    url(r'^login/\?err=(?P<err>.*)$', login_view, name='login_error'),
    url(r'^profile/$', login_required(profile_view), name='profile_view'),
    url(r'^profile/password/$', login_required(tutor_password_change_view), name='password_change'),
    url(r'^groups/$', login_required(AliasesView.as_view()), name='aliases'),
    url(r'^groups/me/$', login_required(MyGroupsView.as_view()), name='groups_view'),
    url(r'^profile/picture/$', login_required(UploadPictureView.as_view()), name='upload_picture_view'),
    url(r'^tutoradmin/$', tutorbest_required(TutorAdminView.as_view()), name='tutor_admin'),
    url(r'^su/(?P<new_user>[^/]*)/$', switch_user),
)
