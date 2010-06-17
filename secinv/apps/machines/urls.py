from django.conf.urls.defaults import patterns, url, include
from . import views

# Regex fragments for easy reading.
machine_slug = r'(?P<machine_slug>[-\w]+)'
section_slug = r'(?P<section_slug>[-\w]+)'
version_number = r'(?P<version_number>[-0-9]+)'
compare_with = r'(?P<compare_with>current|previous)'

urlpatterns = patterns('secinv.apps.machines.views',
    (r'^$', 'index'),
    (r'^search/', 'search'),
    (r'^%s/$' % machine_slug, 'detail'),
#    (r'^%s/history/iptables/%s/(%s/)?$' % (machine_slug, version_number, compare_with), 'history_iptables', {'compare_with': 'previous'}),
    (r'^%s/history/iptables/%s/%s/$' % (machine_slug, version_number, compare_with), 'history_iptables'),
    (r'^%s/history/$' % machine_slug, 'history'),
    (r'^%s/results/$' % machine_slug, 'results'),
)

