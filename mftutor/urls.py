from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mftutor.views.home', name='home'),
    # url(r'^mftutor/', include('mftutor.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', include('mftutor.news.urls'), name='news'),
    url(r'^news/', include('mftutor.news.urls')),
    url(r'^', include('mftutor.page.urls')),
    url(r'^', include('mftutor.tutor.urls')),
    url(r'^events/', include('mftutor.events.urls')),
    url(r'^activation/', include('mftutor.activation.urls')),
    url(r'^email/', include('mftutor.tutormail.urls')),
    url(r'^shirt/', include('mftutor.shirt.urls')),
    url(r'^document/', include('mftutor.documents.urls')),
    url(r'^confirmation/', include('mftutor.confirmation.urls')),
)
