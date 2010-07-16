from django.conf.urls.defaults import patterns, url, include
from . import views

application_id = r'(?P<application_id>[-\w]+)'
assessment_id = r'(?P<assessment_id>[-\w]+)'

urlpatterns = patterns('secinv.apps.webapps.views',
    url(r'^$', 'index', name='webapps-index'),
    url(r'^applications/%s/$' % application_id, 'application', name='application'),
    url(r'^applications/%s/assessments/%s/$' % (application_id, assessment_id), 'assessment', name='assessment'),
)

