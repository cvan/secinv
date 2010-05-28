from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from secinv.machines.models import Machine, Services, System, RPMs, Interface
#from django.http import HttpResponse

import re

def index(request):
    machine_list = Machine.objects.all()
    return render_to_response('machines/index.html', {'machine_list': machine_list},
        context_instance=RequestContext(request))

def detail(request, machine_slug):
    p = get_object_or_404(Machine, hostname=machine_slug)

    system_obj = None
    system_obj = System.objects.filter(machine__id=1).latest()


    services_list = {}
    services_obj = Services.objects.filter(machine__id=p.id).latest()

    if services_obj:
        services_processes = re.split(',', services_obj.processes)
        services_ports = re.split(',', services_obj.ports)

        services_list = dict(zip(services_processes, services_ports))


    rpms_list = []
    rpms_obj = RPMs.objects.filter(machine__id=p.id).latest()

    if rpms_obj:
        rpms_list = re.split('\n', rpms_obj.rpms)


    # Get latest interfaces (select by distinct interface name)
    distinct_interfaces = Interface.objects.filter(machine__id=1).values_list('i_name', flat=True).distinct()

    latest_interfaces = []
    for i in distinct_interfaces:
        latest_distinct = Interface.objects.filter(machine__id=1, i_name=i).latest()
        if latest_distinct:
            latest_interfaces.append(latest_distinct)


    template_context = {'machine': p,
                        'system': system_obj,
                        'services_list': services_list,
                        'rpms': rpms_list,
                        'interfaces': latest_interfaces}
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

