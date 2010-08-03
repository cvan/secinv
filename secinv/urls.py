from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

from django.http import HttpResponsePermanentRedirect

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'secinv.apps.machines.views.index', name='index'),
    (r'^machines/', include('secinv.apps.machines.urls')),
    (r'^webapps/', include('secinv.apps.webapps.urls')),
    (r'^accounts/', include('secinv.apps.accounts.urls')),
    #(r'^search/', include('secinv.apps.haystack.urls')),
    #(r'^fulltext/', include('secinv.fulltext.urls')),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )

