from django.conf.urls.defaults import *
from django.contrib import admin

from django.http import HttpResponsePermanentRedirect

admin.autodiscover()

urlpatterns = patterns('',
    (r'^machines/', include('secinv.apps.machines.urls')),
    (r'^devices/', include('secinv.apps.devices.urls')),
    #(r'^search/', include('secinv.apps.haystack.urls')),
    #(r'^fulltext/', include('secinv.fulltext.urls')),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    # TODO: temporary redirect
    #(r'^', lambda request: HttpResponsePermanentRedirect('/secinv/machines/')),
)

