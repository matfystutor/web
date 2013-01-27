from django.forms import ModelForm, ModelChoiceField, DateTimeField
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render, redirect, render_to_response
from django.template import RequestContext
from news.models import NewsPost
from django.core.urlresolvers import reverse
from datetime import datetime
from tutor.auth import tutorbest_required
from django.contrib.auth.models import User
from mftutor.settings import YEAR
from datetime import datetime

class AuthorModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name()

class NewsView(TemplateView):
    template_name = 'news.html'

    def get(self, request, year=None, month=None, day=None, pk=None):
        news_list = NewsPost.objects.order_by('-posted').select_related()

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

        params = {
                'news_list': news_list,
                'year': year,
                'month': month,
                'day': day,
                }
        return self.render_to_response(params)

class NewsCreateView(CreateView):
    model = NewsPost
    template_name = "newsform.html"

    def get_form(self, form_class):
        f = form_class(**self.get_form_kwargs())
        f.fields['author'] = AuthorModelChoiceField(
                label = 'Forfatter',
                empty_label = None,
                queryset = User.objects.filter(tutorprofile__tutor__groups__handle='best',
                    tutorprofile__tutor__year__in=[YEAR]))
        return f

    def get_context_data(self, **kwargs):
        d = super(NewsCreateView, self).get_context_data(**kwargs)
        d['create'] = True
        return d

    def get_initial(self):
        initial = super(NewsCreateView, self).get_initial()
        initial = initial.copy()
        initial['author'] = self.request.user
        initial['posted'] = datetime.now()
        return initial

    def get_success_url(self):
        return reverse("news")

    @method_decorator(tutorbest_required)
    def dispatch(self, *args, **kwargs):
        return super(NewsCreateView, self).dispatch(*args, **kwargs)

class NewsUpdateView(UpdateView):
    model = NewsPost
    template_name = "newsform.html"

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
