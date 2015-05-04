# coding: utf-8
from django import forms
from django.forms.extras import SelectDateWidget
from django.views.generic import UpdateView, TemplateView, CreateView, DeleteView
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from ..settings import YEAR
from .models import Document
from ..tutor.auth import tutorbest_required, tutor_required

class UploadDocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('title', 'year', 'published', 'type', 'doc_file')

    published = forms.DateField(widget=SelectDateWidget(years=range(1970,YEAR+1)),
            label='Dato',
            initial=Document._meta.get_field('published').default)


class UploadDocumentView(CreateView):
    model = Document
    template_name = "documentuploader.html"
    form_class = UploadDocumentForm

    def get_success_url(self):
        return reverse("list_"+self.object.type)

    @method_decorator(tutorbest_required)
    def dispatch(self, *args, **kwargs):
        return super(UploadDocumentView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        d = super(UploadDocumentView, self).get_context_data(**kwargs)
        d['create'] = True
        return d     

class EditDocumentView(UpdateView):
    model = Document
    template_name = "documentuploader.html"
    form_class = UploadDocumentForm

    def get_success_url(self):
        return reverse("list_"+self.object.type)

    @method_decorator(tutorbest_required)
    def dispatch(self, *args, **kwargs):
        return super(EditDocumentView, self).dispatch(*args, **kwargs)
    def get_context_data(self, **kwargs):
        d = super(EditDocumentView, self).get_context_data(**kwargs)
        d['create'] = False
        return d

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
