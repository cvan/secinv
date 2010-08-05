from django.conf.urls.defaults import *
from .views import SearchView

urlpatterns = patterns('apps.haystack.views',
    url(r'^$', SearchView(), name='haystack_search'),
)
