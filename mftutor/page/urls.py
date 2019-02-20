from django.conf.urls import url
from django.views.generic import TemplateView

urlpatterns = [url('^' + x + '/', TemplateView.as_view(template_name=x + '.html'), name=x) for x in (
    'vedtaegter',
    'gruppekatalog',
    'rus2tur',
    'sponsor',
    'kontakt',
    'todo',
    'intro',
    'gallery',
    'feeds',
)]
