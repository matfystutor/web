from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView, DeleteView
from news.models import NewsPost
from news.views import NewsCreateView, NewsUpdateView
from tutor.auth import tutorbest_required
from django.core.urlresolvers import reverse_lazy

urlpatterns = patterns('',
    url(r'^$',
        ListView.as_view(
            queryset=NewsPost.objects.order_by('-posted'),
            template_name="news.html",
            context_object_name="news_list"),
        name='news'),
    url(r'^add/$', NewsCreateView.as_view(), name='news_add'),
    url(r'^edit/(?P<pk>\d+)/$', NewsUpdateView.as_view(), name='news_edit'),
    url(r'^delete/(?P<pk>\d+)/$',
        tutorbest_required(DeleteView.as_view(model=NewsPost, success_url=reverse_lazy('news'))),
        name='news_delete'),
)
