from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from .views import register_view, activate_view

urlpatterns = patterns('',
    url(r'^$', register_view, name='register'),
    url(r'^(?P<activation_key>[0-9a-f]{8,})/$', activate_view, name='activate'),
    url(r'^thanks/$', TemplateView.as_view(template_name='activation/thanks.html'), name='activation_thanks'),
    url(r'^activated/$', TemplateView.as_view(template_name='activation/activated.html'), name='activation_activated'),
)
