from django.db.models import Q
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from .models import Machine, Services, System, RPMs, Interface, SSHConfig, IPTableInfo
from .forms import MachineSearchForm
from .utils import diff_list, diff_dict, get_version_diff, get_version_diff_field

from reversion.models import Version

import re


def index(request):
    """Machines index page."""
    machines = Machine.objects.all()
    query = request.GET.get('q', '')
    return render_to_response('machines/index.html',
        {'machines': machines, 'query': query},
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

    ## System.
    system_latest = []
    system_history = System.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()

    # Get historical versions of System objects.
    system_versions = get_version_diff(system_history[0])

    if system_history.exists():
        system_latest = system_history[0]


    ## Services.
    services_latest = []
    services_history = Services.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()

    # Get historical versions of Services objects.
    services_versions = get_version_diff(services_history[0], ',')

    if services_history.exists():
        services_latest = services_history[0]


    ## Interfaces.

    # Get latest interfaces (select by distinct interface name).
    distinct_interfaces = Interface.objects.filter(
        machine__id=p.id).values_list('i_name', flat=True).distinct()

    interfaces_latest = []
    interfaces_versions = []
    for i in distinct_interfaces:
        i_latest = Interface.objects.filter(machine__id=p.id,
                                            i_name=i).latest()
        interfaces_latest.append(i_latest)

        # Append each unique interface's history.
        i_v = get_version_diff(i_latest)
        interfaces_versions += i_v

    interfaces_versions = sorted(interfaces_versions,
                                 key=lambda k: k['timestamp'], reverse=True)


    ## SSHConfig.
    sshconfig_latest = []
    sshconfig_history = SSHConfig.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()

    # Get historical versions of SSHConfig objects.
    sshconfig_versions = get_version_diff(sshconfig_history[0], '\n')

    if sshconfig_history.exists():
        sshconfig_latest = sshconfig_history[0]


    # RPMs.
    rpms_list = []
    rpms_date_added = None
    rpms_history = RPMs.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()

    # Get historical versions of RPMs objects.
    rpms_versions = get_version_diff(rpms_history[0], '\n')

    if rpms_history.exists():
        rpms_list = re.split('\n', rpms_history[0].v_rpms)
        rpms_date_added = rpms_history[0].date_added

    rpms_latest = {'installed': rpms_list, 'date_added': rpms_date_added}


    ## iptables.
    iptables_latest = []
    iptables_history = IPTableInfo.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()

    # Get historical versions of IPTableInfo objects.
    iptables_versions = get_version_diff_field(iptables_history[0], 'body')

    if iptables_history.exists():
        iptables_latest = iptables_history[0]


    template_context = {'query': query,
                        'machine': p,
                        'system': system_latest,
                        'system_versions': system_versions,
                        'services': services_latest,
                        'services_versions': services_versions,
                        'rpms': rpms_latest,
                        'rpms_versions': rpms_versions,
                        'interfaces': interfaces_latest,
                        'interfaces_versions': interfaces_versions,
                        'sshconfig': sshconfig_latest,
                        'sshconfig_versions': sshconfig_versions,
                        'iptables': iptables_latest,
                        'iptables_versions': iptables_versions}
    return render_to_response('machines/detail.html', template_context,
        context_instance=RequestContext(request))


def results(request, machine_slug):
    p = get_object_or_404(Machine, hostname=machine_slug)
    return render_to_response('machines/results.html', {'machine': p},
        context_instance=RequestContext(request))


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


def history_iptables(request, machine_slug):
    m = get_object_or_404(Machine, hostname=machine_slug)
    query = request.GET.get('q', '')

    iptables_current = ''
    iptables_previous = ''

    iptables_history = IPTableInfo.objects.filter(machine__id=m.id).order_by(
        '-date_added').all()

    if iptables_history.exists():
        iptables_current = iptables_history[0].body

        obj_versions = Version.objects.get_for_object(
            iptables_history[0]).order_by('-revision')
        if obj_versions:
            iptables_previous = obj_versions[0].field_dict['body']


    template_context = {'machine': m,
                        'query': query,
                        'iptables_current': iptables_current,
                        'iptables_previous': iptables_previous}
    return render_to_response('machines/iptables.html', template_context,
        context_instance=RequestContext(request))

