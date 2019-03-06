from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import ProfileView, RusClassView, GroupView, SearchView

urlpatterns = [
    path('search/', login_required(SearchView.as_view()),
        name='browser_search'),
    path('profile/<studentnumber>/', login_required(ProfileView.as_view()),
        name='browser_profile'),
    path('rusclass/<int:year>/<handle>/', login_required(RusClassView.as_view()),
        name='browser_rusclass'),
    path('group/<int:year>/<handle>/', login_required(GroupView.as_view()),
        name='browser_group'),
]
