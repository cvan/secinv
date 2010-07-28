from django.db.models import Q
from django.core import serializers
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, \
                        HttpResponseNotFound, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson

from .models import Assessment, Application


@login_required
def index(request):
    """Web Applications index page."""
    applications = Application.objects.all()
    query = request.GET.get('q', '')

    template_context = {'query': query,
                        'applications': applications,}
    return render_to_response('webapps/index.html', template_context,
                              context_instance=RequestContext(request))

@login_required
def application(request, application_id):
    a = get_object_or_404(Application, id=application_id)
    applications = Application.objects.all()
    query = request.GET.get('q', '')

    template_context = {'query': query,
                        'applications': applications,
                        'application': a,}
    return render_to_response('webapps/application.html', template_context,
                              context_instance=RequestContext(request))

@login_required
def assessment(request, application_id, assessment_id):
    assessment = get_object_or_404(Assessment, id=application_id)
    application = get_object_or_404(Application, id=assessment.id)
    applications = Application.objects.all()
    query = request.GET.get('q', '')

    template_context = {'query': query,
                        'applications': applications,
                        'assessment': assessment,
                        'application': application,}
    return render_to_response('webapps/assessment.html', template_context,
                              context_instance=RequestContext(request))
