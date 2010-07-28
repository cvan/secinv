from django.http import HttpResponse, HttpResponseRedirect, \
                        HttpResponseNotFound, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django.contrib.auth.decorators import login_required


def index(request):
    """Machines index page."""
    query = request.GET.get('q', '')

    template_context = {}
    return render_to_response('login/index.html', template_context,
                              context_instance=RequestContext(request))


'''
return HttpResponseRedirect(destination)
'''

