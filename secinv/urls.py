from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^machines/', include('secinv.apps.machines.urls')),
    (r'^search/', include('secinv.apps.haystack.urls')),
    #(r'^search/', include('secinv.haystack_search.urls')),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)

