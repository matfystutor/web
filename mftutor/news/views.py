import datetime
from django.views.generic.base import TemplateResponseMixin
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView, View
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render, redirect, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from ..tutor.auth import tutorbest_required
from ..settings import YEAR
from .forms import AuthorModelChoiceField, NewsPostForm
from .models import NewsPost

class BaseNewsView(View):
    def get_group_handle(self):
        raise ImproperlyConfigured("BaseNewsView descendant needs to override get_group_handle")

    def get_queryset(self):
        return NewsPost.objects.filter(group_handle__exact=self.get_group_handle())

    def get_context_data(self, **kwargs):
        return kwargs

    def get(self, request, year=None, month=None, day=None, pk=None):
        news_list = self.get_queryset().order_by('-posted').select_related()

        if pk:
            news_list = news_list.filter(pk=pk)
        elif day:
            news_list = news_list.filter(posted__year=year,
                    posted__month=month,
                    posted__day=day)
        elif month:
            news_list = news_list.filter(posted__year=year,
                    posted__month=month)
        elif year:
            news_list = news_list.filter(posted__year=year)
        else:
            # TODO We should probably have a year-field in the news posts
            news_list = news_list.filter(posted__gte=datetime.date(YEAR - 1, 11, 1))

        params = {
                'news_list': news_list,
                'year': year,
                'month': month,
                'day': day,
                }
        return self.render_to_response(self.get_context_data(**params))

class NewsView(BaseNewsView, TemplateResponseMixin):
    template_name = 'news.html'

    def get_group_handle(self):
        return u'alle'

class NewsCreateView(CreateView):
    model = NewsPost
    template_name = "newsform.html"
    form_class = NewsPostForm

    def get_context_data(self, **kwargs):
        d = super(NewsCreateView, self).get_context_data(**kwargs)
        d['create'] = True
        d['group_handles'] = [{'handle': handle, 'name': name} for handle, name in NewsPost.GROUP_HANDLES]
        return d

    def get_initial(self):
        initial = super(NewsCreateView, self).get_initial()
        initial = initial.copy()
        initial['author'] = self.request.user
        initial['posted'] = datetime.datetime.now()
        initial['group_handle'] = u'alle'
        return initial

    def get_success_url(self):
        return reverse("news")

    @method_decorator(tutorbest_required)
    def dispatch(self, *args, **kwargs):
        return super(NewsCreateView, self).dispatch(*args, **kwargs)

class NewsUpdateView(UpdateView):
    model = NewsPost
    template_name = "newsform.html"
    form_class = NewsPostForm

    def get_form(self, form_class):
        f = form_class(**self.get_form_kwargs())
        f.fields['author'] = AuthorModelChoiceField(
                label = 'Forfatter',
                empty_label = None,
                queryset = User.objects.filter(tutorprofile__tutor__groups__handle='best',
                    tutorprofile__tutor__year__in=[YEAR]))
        return f

    def get_success_url(self):
        return reverse("news")

    @method_decorator(tutorbest_required)
    def dispatch(self, *args, **kwargs):
        return super(NewsUpdateView, self).dispatch(*args, **kwargs)
