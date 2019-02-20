from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy

from .feed import NewsFeed
from .views import *

urlpatterns = [
    url(r'^(?:(?P<year>\d+)/(?:(?P<month>\d+)/(?:(?P<day>\d+)/(?:(?P<pk>\d+)/)?)?)?)?$',
        NewsView.as_view(), name='news'),
    url(r'^add/$', NewsCreateView.as_view(), name='news_add'),
    url(r'^edit/(?P<pk>\d+)/$', NewsUpdateView.as_view(), name='news_edit'),
    url(r'^delete/(?P<pk>\d+)/$',
        tutorbest_required(DeleteView.as_view(model=NewsPost, success_url=reverse_lazy('news'))),
        name='news_delete'),
    url(r'^feed/$', NewsFeed(), name='news_feed'),
]
