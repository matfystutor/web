from django.urls import reverse_lazy, path, re_path
from django.views.generic import DeleteView

from .feed import NewsFeed
from .views import *

urlpatterns = [
    re_path(r'^(?:(?P<year>\d+)/(?:(?P<month>\d+)/(?:(?P<day>\d+)/(?:(?P<pk>\d+)/)?)?)?)?$',
        NewsView.as_view(), name='news'),
    path('add/', NewsCreateView.as_view(), name='news_add'),
    path('edit/<int:pk>/', NewsUpdateView.as_view(), name='news_edit'),
    path('delete/<int:pk>/',
        tutorbest_required(DeleteView.as_view(model=NewsPost, success_url=reverse_lazy('news'))),
        name='news_delete'),
    path('feed/', NewsFeed(), name='news_feed'),
]
