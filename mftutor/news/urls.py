from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView, DeleteView
from django.core.urlresolvers import reverse_lazy
from ..tutor.auth import tutorbest_required
from .feed import NewsFeed
from .models import NewsPost
from .views import *

urlpatterns = patterns('',
    url(r'^(?:(?P<year>\d+)/(?:(?P<month>\d+)/(?:(?P<day>\d+)/(?:(?P<pk>\d+)/)?)?)?)?$',
        NewsView.as_view(), name='news'),
    url(r'^add/$', NewsCreateView.as_view(), name='news_add'),
    url(r'^edit/(?P<pk>\d+)/$', NewsUpdateView.as_view(), name='news_edit'),
    url(r'^delete/(?P<pk>\d+)/$',
        tutorbest_required(DeleteView.as_view(model=NewsPost, success_url=reverse_lazy('news'))),
        name='news_delete'),
    url(r'^feed/$', NewsFeed(), name='news_feed'),
)
