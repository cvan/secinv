from django.conf.urls.defaults import *
from .views import SearchView


urlpatterns = patterns('secinv.apps.haystack.views',
    url(r'^$', SearchView(), name='haystack_search'),
)
