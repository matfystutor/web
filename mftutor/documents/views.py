# coding: utf-8
import copy
import datetime

from django import forms
from django.forms.extras import SelectDateWidget
from django.views.generic import UpdateView, TemplateView, CreateView, DeleteView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import ModelFormMixin
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from .models import Document
from ..tutor.auth import tutorbest_required, tutor_required

class UploadDocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('title', 'year', 'published', 'type', 'doc_file')

    # TODO get year from request
    published = forms.DateField(
        widget=SelectDateWidget(years=[]),
        label='Dato')

    def __init__(self, **kwargs):
        year = kwargs.pop('year')
        initial = copy.deepcopy(kwargs.pop('initial', {}))
        initial.setdefault('year', year)
        initial.setdefault('published', datetime.date.today())
        kwargs['initial'] = initial
        super(UploadDocumentForm, self).__init__(**kwargs)
        self.fields['published'].widget.years = range(1970, year + 1)


class UploadDocumentFormMixin(TemplateResponseMixin, ModelFormMixin):
    model = Document
    template_name = "documentuploader.html"
    form_class = UploadDocumentForm

    def get_success_url(self):
        return reverse("list_"+self.object.type)

    @method_decorator(tutorbest_required)
    def dispatch(self, *args, **kwargs):
        return super(UploadDocumentFormMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        d = super(UploadDocumentFormMixin, self).get_context_data(**kwargs)
        if isinstance(self, CreateView):
            d['create'] = True
        else:
            d['create'] = False
        return d

    def get_form_kwargs(self):
        kwargs = super(UploadDocumentFormMixin, self).get_form_kwargs()
        kwargs['year'] = self.request.year
        return kwargs


class UploadDocumentView(CreateView, UploadDocumentFormMixin):
    pass


class EditDocumentView(UpdateView, UploadDocumentFormMixin):
    pass


class DeleteDocumentView(DeleteView):
    model=Document

    def get_success_url(self):
        return reverse("list_"+self.object.type)

    @method_decorator(tutorbest_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteDocumentView, self).dispatch(*args, **kwargs)


class DocumentListView(TemplateView):
    def get_queryset(self):
        return Document.objects.filter(type__exact=self.kind)

    def get(self, request, year=None):
        document_list = self.get_queryset()
        if year:        
            document_list = document_list.filter(year=year)
        params = {
                 "document_list":document_list,
                 "kind":self.kind,
                 "year":year
        }        
        return self.render_to_response(params)

    @method_decorator(tutor_required)
    def dispatch(self, *args, **kwargs):
        return super(DocumentListView, self).dispatch(*args, **kwargs)

    def get_template_names(self):
        return ('documents/' + self.kind + '.html',)


class GuidesView(DocumentListView):
    kind = 'guides'

class MinutesView(DocumentListView):
    kind = 'referater'

    def get_queryset(self):
        return Document.referater.all()

class PublicationsView(DocumentListView):
    kind = 'udgivelser'
