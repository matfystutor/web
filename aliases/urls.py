from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from aliases.views import *

urlpatterns = patterns('',
    url(r'^$', login_required(aliases_view), name='aliases'),
)
