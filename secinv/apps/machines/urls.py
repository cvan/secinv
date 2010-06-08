from django.conf.urls.defaults import patterns, url, include
from . import views

# Regex fragments for easy reading.
machine_slug = r'(?P<machine_slug>[-\w]+)'

urlpatterns = patterns('secinv.apps.machines.views',
    (r'^$', 'index'),
    (r'^search/', 'search'),
    (r'^%s/$' % machine_slug, 'detail'),
    (r'^%s/history/$' % machine_slug, 'history'),
    (r'^%s/results/$' % machine_slug, 'results'),
    (r'^%s/vote/$' % machine_slug, 'vote'),
)

