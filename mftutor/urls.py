import django.views.static
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.urls import path

from mftutor.reg.views import burtavle_frameset, burtavle

admin.autodiscover()

urlpatterns = [
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    path('admin/', admin.site.urls),
    path('news/', include('mftutor.news.urls')),
    path('', include('mftutor.page.urls')),
    path('gallery/', include('mftutor.gallery.urls')),
    path('', include('mftutor.tutor.urls')),
    path('groups/', include('mftutor.groups.urls')),
    path('signup/', include('mftutor.signup.urls')),
    path('events/', include('mftutor.events.urls')),
    path('email/', include('mftutor.tutormail.urls')),
    path('shirt/', include('mftutor.shirt.urls')),
    path('document/', include('mftutor.documents.urls')),
    path('confirmation/', include('mftutor.confirmation.urls')),
    path('rus/', include('mftutor.rus.urls')),
    path('reg/', include('mftutor.reg.urls')),
    path('burtavle/frame/', burtavle, name="burtavle"),
    path('burtavle/', burtavle_frameset, name="burtavle_frameset"),
    path('dump/', include('mftutor.dump.urls')),
    path('browser/', include('mftutor.browser.urls')),
    path('tutorhold/', include('mftutor.rusclass.urls')),
    path('tutorbog/', include('mftutor.tutorbog.urls')),
    path('gf/', include('mftutor.gf.urls')),
]

try:
    import debug_toolbar
except ImportError:
    pass
else:
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

if settings.DEBUG:
    # Temporary media (user uploaded static files)
    # serving from dev server
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
