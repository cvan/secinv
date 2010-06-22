from django.conf.urls.defaults import patterns, url, include
from . import views

# Regex fragments for easy reading.
machine_slug = r'(?P<machine_slug>[-\w]+)'
section_slug = r'(?P<section_slug>[-\w]+)'
version_number = r'(?P<version_number>[0-9]+)'
compare_with = r'(?P<compare_with>current|previous)'
ac_id = r'(?P<ac_id>[0-9]+)'
directive_slug = r'(?P<directive_slug>[-\w]+)'

urlpatterns = patterns('secinv.apps.machines.views',
    url(r'^$', 'index', name='machines-index'),
    url(r'^search/', 'search', name='machines-search'),

    url(r'^filters/$', 'machine_filter', name='machine-filter'),

    url(r'^%s/$' % machine_slug, 'detail', name='machines-detail'),

    url(r'^filters/httpd-conf/results/$', 'ac_filter_results', name='ac-filter-results'),

    url(r'^filters/httpd-conf/directive/$', 'ac_filter_directives', name='ac-filter-directives'),
    url(r'^filters/httpd-conf/$', 'ac_filter_directives_keys', name='ac-filter-directives-all'),

#    url(r'^%s/history/iptables/%s/(%s/)?$' % (machine_slug, version_number, compare_with), 'history_iptables', {'compare_with': 'previous'}, name='history-iptables'),

    url(r'^%s/httpd-conf/%s/$' % (machine_slug, ac_id), 'httpd_conf', name='httpd-conf'),

#    url(r'^%s/diff/iptables/%s/%s/$' % (machine_slug, version_number, compare_with), 'diff_iptables', name='diff-iptables'),
#    url(r'^%s/diff/httpd-conf/%s/%s/$' % (machine_slug, version_number, compare_with), 'diff_httpd_conf', name='diff-httpd-conf'),

    url(r'^%s/diff/%s/%s/%s/$' % (machine_slug, section_slug, version_number, compare_with), 'diff', name='diff'),

    url(r'^%s/history/$' % machine_slug, 'history', name='history'),
)

