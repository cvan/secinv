from django.conf.urls.defaults import patterns, url, include
from . import views

machine_slug = r'(?P<machine_slug>[-\w]+)'

urlpatterns = patterns('apps.machines.views',
    (r'^$', 'index'),
    (r'^%s/$' % machine_slug, 'detail'),
)

