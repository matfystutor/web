from django.views.generic.base import TemplateResponseMixin
from ..news.views import BaseNewsView

class RusNewsView(BaseNewsView, TemplateResponseMixin):
    template_name = 'rus/nyheder.html'

    def get_group_handle(self):
        return u'rus'

