from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
from tutor.models import Tutor, TutorGroup, BoardMember
from tutor.views import logout_view, login_view, profile_view, GroupsView, tutor_password_change_view, UploadPictureView
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^tutors/$', login_required(
        ListView.as_view(
            queryset=Tutor.objects.filter(year=2012, early_termination__isnull=True).order_by('profile__user__first_name'),
            template_name="tutors.html",
            context_object_name="tutor_list")),
        name='tutors'),
    url(r'^board/$',
        ListView.as_view(
            queryset=BoardMember.objects.filter(tutor__year=2012),
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
