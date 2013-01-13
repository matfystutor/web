from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
from tutor.models import Tutor, TutorGroup, BoardMember
from tutor.views import logout_view, login_view, profile_view, GroupsView, tutor_password_change_view, UploadPictureView, tutors_view
from django.contrib.auth.decorators import login_required
from mftutor import siteconfig

urlpatterns = patterns('',
    url(r'^tutors/$', login_required(tutors_view), name='tutors'),
    url(r'^tutors/(?P<group>[^/?]+)/$', login_required(tutors_view)),
    url(r'^board/$',
        ListView.as_view(
            queryset=BoardMember.objects.filter(tutor__year=siteconfig.year).select_related(),
            template_name="board.html",
            context_object_name="tutor_list"),
        name='board'),
    url(r'^logout/$', logout_view),
    url(r'^login/$', login_view),
    url(r'^login/\?err=(?P<err>.*)$', login_view, name='login_error'),
    url(r'^profile/$', login_required(profile_view), name='profile_view'),
    url(r'^profile/password/$', login_required(tutor_password_change_view), name='password_change'),
    url(r'^groups/$', login_required(GroupsView.as_view()), name='groups_view'),
    url(r'^profile/picture/$', login_required(UploadPictureView.as_view()), name='upload_picture_view'),
)
