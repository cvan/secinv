from django.conf.urls.defaults import patterns, url, include
from . import views

# Regex fragments for easy reading.
device_slug = r'(?P<device_slug>[-\w]+)'

urlpatterns = patterns('secinv.apps.devices.views',
    (r'^$', 'index'),
    (r'^search/', 'search'),
    (r'^%s/$' % device_slug, 'detail'),
    (r'^%s/results/$' % device_slug, 'results'),
    (r'^%s/vote/$' % device_slug, 'vote'),
)

