from django.conf.urls import patterns, url
#from django.views.generic import DetailView, ListView
from activation.views import register_view, activate_view
#from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^$', register_view, name='register'),
    url(r'^([0-9a-f]{8,})/$', activate_view, name='activate'),
    url(r'^thanks/$', TemplateView.as_view(template_name='activation/thanks.html'), name='activation_thanks'),
    url(r'^activated/$', TemplateView.as_view(template_name='activation/activated.html'), name='activation_activated'),
)
