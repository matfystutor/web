from django.views.generic import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from news.models import NewsPost
from django.core.urlresolvers import reverse
from datetime import datetime
from tutor.auth import tutorbest_required

class NewsCreateView(CreateView):
    model = NewsPost
    template_name = "newsform.html"

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
        return super(CreateView, self).dispatch(*args, **kwargs)

class NewsUpdateView(UpdateView):
    model = NewsPost
    template_name = "newsform.html"

    def get_success_url(self):
        return reverse("news")

    @method_decorator(tutorbest_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateView, self).dispatch(*args, **kwargs)
