from django.conf.urls.defaults import patterns, url, include
from . import views

# Regex fragments for easy reading.
machine_slug = r'(?P<machine_slug>[-\w]+)'

urlpatterns = patterns('secinv.apps.machines.views',
    (r'^$', 'index'),
    (r'^%s/$' % machine_slug, 'detail'),
)

