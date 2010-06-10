from django.db.models import Q
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from .models import Machine, Services, System, RPMs, Interface, SSHConfig
from .forms import MachineSearchForm

import re


def index(request):
    machine_list = Machine.objects.all()
    query = request.GET.get('q', '')
    return render_to_response('machines/index.html',
        {'machine_list': machine_list, 'query': query},
        context_instance=RequestContext(request))


# View that that returns the JSON result.
def history(request, machine_slug):
    # TODO: prevent calls
    #if not request.is_ajax():
    #    return HttpResponse(status=400)

    p = get_object_or_404(Machine, hostname=machine_slug)

    # Retrieve all the system history.
    system_history = System.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()

    # Serialize the result of the database retrieval to JSON and send an
    # application/json response.
    return HttpResponse(serializers.serialize('json', system_history),
                        mimetype='application/json')


def detail(request, machine_slug):
    p = get_object_or_404(Machine, hostname=machine_slug)
    query = request.GET.get('q', '')

    system_latest = []
    system_history = System.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()

    if system_history.exists():
        system_latest = System.objects.filter(machine__id=p.id).latest()


    services_latest = []
    services_history = Services.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()

    if services_history.exists():
        services_latest = Services.objects.filter(machine__id=p.id).latest()


    rpms_list = []
    rpms_date_added = None
    rpms_history = RPMs.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()

    if rpms_history.exists():
        rpms_obj = RPMs.objects.filter(machine__id=p.id).latest()

        rpms_list = re.split('\n', rpms_obj.rpms)

        rpms_date_added = rpms_obj.date_added

    rpms_latest = {'installed': rpms_list, 'date_added': rpms_date_added}


    # Get latest interfaces (select by distinct interface name).
    distinct_interfaces = Interface.objects.filter(
        machine__id=p.id).values_list('i_name', flat=True).distinct()

    interfaces_latest = []
    interfaces_added_ids = []
    for i in distinct_interfaces:
        i_latest = Interface.objects.filter(machine__id=p.id,
                                            i_name=i).latest()
        interfaces_latest.append(i_latest)

        i_oldest = Interface.objects.filter(machine__id=p.id,
            i_name=i).order_by('date_added').all()
        if i_oldest.exists():
            interfaces_added_ids.append(i_oldest[0].id)

        i_previous = Interface.objects.filter(machine__id=p.id,
            i_name=i, active=False).exclude(id=i_latest.id).order_by(
            '-date_added').all()
        if i_previous.exists():
            # If second most recent interface was inactive but the latest
            # interface is now active, then mark it as "added."
            interfaces_added_ids.append(i_latest.id)

    interfaces_history = Interface.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()


    sshconfig_latest = []
    sshconfig_history = SSHConfig.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()

    if sshconfig_history.exists():
        sshconfig_latest = SSHConfig.objects.filter(machine__id=p.id).latest()


    template_context = {'query': query,
                        'machine': p,
                        'system': system_latest,
                        'system_history': system_history,
                        'services': services_latest,
                        'services_history': services_history,
                        'rpms': rpms_latest,
                        'rpms_history': rpms_history,
                        'interfaces': interfaces_latest,
                        'interfaces_history': interfaces_history,
                        'interfaces_added': interfaces_added_ids,
                        'sshconfig': sshconfig_latest,
                        'sshconfig_history': sshconfig_history}
    return render_to_response('machines/detail.html', template_context,
        context_instance=RequestContext(request))


def results(request, machine_slug):
    p = get_object_or_404(Machine, hostname=machine_slug)
    return render_to_response('machines/results.html', {'machine': p},
        context_instance=RequestContext(request))


def vote(request, machine_slug):
    '''
    p = get_object_or_404(Machine, hostname=machine_slug)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the machine voting form.
        return render_to_response('machines/detail.html', {
            'machine': p,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('secinv.machines.views.results',
            args=(p.id,)))
    '''
    pass


def search(request):
    query = request.GET.get('q', '')
    terms = query.split()
    results = []
    excerpts = {}

    if query:
        form = MachineSearchForm(request.GET)
        if form.is_valid():
            results = form.get_result_queryset()
    else:
        form = MachineSearchForm()

    template_context = {'form': form,
                        'results': results,
                        'query': query,
                        'terms': terms}
    return render_to_response('machines/search.html', template_context,
        context_instance=RequestContext(request))
