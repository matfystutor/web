from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [path(x + '/', TemplateView.as_view(template_name=x + '.html'), name=x) for x in (
    'vedtaegter',
    'gruppekatalog',
    'rus2tur',
    'kontakt',
    'todo',
    'intro',
    'gallery',
    'feeds',
    'GDPR',

)]
