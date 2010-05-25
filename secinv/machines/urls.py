from django.conf.urls.defaults import *

urlpatterns = patterns('secinv.machines.views',
    (r'^$', 'index'),
    (r'^(?P<machine_id>\d+)/$', 'detail'),
    (r'^(?P<machine_id>\d+)/results/$', 'results'),
    (r'^(?P<machine_id>\d+)/vote/$', 'vote'),
)

