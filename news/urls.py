from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
from news.models import NewsPost
from news.views import NewsCreateView
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^$',
        ListView.as_view(
            queryset=NewsPost.objects.order_by('-posted'),
            template_name="news.html",
            context_object_name="news_list"),
        name='news'),
    url(r'^add/$', NewsCreateView.as_view()),
)
