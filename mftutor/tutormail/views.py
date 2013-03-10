# encoding: utf-8

from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateResponseMixin
from .models import Email

class EmailListView(ListView, TemplateResponseMixin):
    model = Email
    template_name = 'email_list.html'

    def get_queryset(self):
        return Email.objects.filter(archive=False)

class EmailDetailView(DetailView, TemplateResponseMixin):
    model = Email
    template_name = 'email_detail.html'
