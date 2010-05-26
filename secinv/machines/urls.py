from django.conf.urls.defaults import *

# Regex fragments for easy reading.
machine_slug = r'(?P<machine_slug>[-\w]+)'

urlpatterns = patterns('secinv.machines.views',
    (r'^$', 'index'),
    (r'^%s/$' % machine_slug, 'detail'),
    (r'^%s/results/$' % machine_slug, 'results'),
    (r'^%s/vote/$' % machine_slug, 'vote'),

#    (r'^(?P<machine_slug>[-\w]+)/$', 'detail'),
#    (r'^(?P<machine_slug>[-\w]+)/results/$', 'results'),
#    (r'^(?P<machine_slug>[-\w]+)/vote/$', 'vote'),

)

