from django.conf.urls.defaults import *
from .views import SearchView


urlpatterns = patterns('secinv.haystack_search.views',
    url(r'^$', SearchView(), name='haystack_search'),
)
