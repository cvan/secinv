from django.conf.urls.defaults import patterns, url, include
from . import views

# Regex fragments for easy reading.
machine_slug = r'(?P<machine_slug>[-\w]+)'
section_slug = r'(?P<section_slug>[-\w]+)'
version_number = r'(?P<version_number>[0-9]+)'
compare_with = r'(?P<compare_with>current|previous)'
ac_id = r'(?P<ac_id>[0-9]+)'

urlpatterns = patterns('secinv.apps.machines.views',
    url(r'^$', 'index', name='machines-index'),
    url(r'^search/', 'search', name='machines-search'),
    url(r'^%s/$' % machine_slug, 'detail', name='machines-detail'),
#    url(r'^%s/history/iptables/%s/(%s/)?$' % (machine_slug, version_number, compare_with), 'history_iptables', {'compare_with': 'previous'}, name='history-iptables'),
    url(r'^%s/httpdconf/%s/$' % (machine_slug, ac_id), 'httpd_conf', name='httpd-conf'),
    url(r'^%s/history/iptables/%s/%s/$' % (machine_slug, version_number, compare_with), 'history_iptables', name='history-iptables'),
    url(r'^%s/history/$' % machine_slug, 'history', name='history'),
)

