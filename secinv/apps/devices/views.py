from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from .models import Device
#from .models import Device, Services, System, RPMs, Interface

from .forms import DeviceSearchForm

#from django.http import HttpResponse

import re

def index(request):
    device_list = Device.objects.all()
    query = request.GET.get('q', '')
    return render_to_response('devices/index.html',
        {'device_list': device_list, 'query': query},
        context_instance=RequestContext(request))


def detail(request, device_slug):
    p = get_object_or_404(Device, hostname=device_slug)
    query = request.GET.get('q', '')

	# System.
    system_latest = []
    system_history = System.objects.filter(device__id=p.id).order_by(
        '-date_added').all()

    if system_history.exists():
        system_latest = System.objects.filter(device__id=p.id).latest()


	# Services.
    services_latest = []
    services_history = Machine.Services.objects.filter(device__id=p.id).order_by(
        '-date_added').all()

    if services_history.exists():
        services_latest = Machine.Services.objects.filter(device__id=p.id).latest()


	# RPMs.
    rpms_list = []
    rpms_date_added = None
    rpms_history = RPMs.objects.filter(device__id=p.id).order_by(
        '-date_added').all()

    if rpms_history.exists():
        rpms_obj = RPMs.objects.filter(device__id=p.id).latest()

        rpms_list = re.split('\n', rpms_obj.rpms)

        rpms_date_added = rpms_obj.date_added

    rpms_latest = {'installed': rpms_list, 'date_added': rpms_date_added}


	# Interfaces.

    # Get latest interfaces (select by distinct interface name).
    distinct_interfaces = Interface.objects.filter(
        device__id=p.id).values_list('i_name', flat=True).distinct()

    interfaces_latest = []
    interfaces_added_ids = []
    for i in distinct_interfaces:
        i_latest = Interface.objects.filter(device__id=p.id,
                                            i_name=i).latest()
        interfaces_latest.append(i_latest)

        i_oldest = Interface.objects.filter(device__id=p.id,
            i_name=i).order_by('date_added').all()
        if i_oldest.exists():
            interfaces_added_ids.append(i_oldest[0].id)

        i_previous = Interface.objects.filter(device__id=p.id,
            i_name=i, active=False).exclude(id=i_latest.id).order_by(
            '-date_added').all()
        if i_previous.exists():
            # If second most recent interface was inactive but the latest
            # interface is now active, then mark it as "added."
            interfaces_added_ids.append(i_latest.id)

    interfaces_history = Interface.objects.filter(device__id=p.id).order_by(
        '-date_added').all()

    template_context = {'query': query,
                        'device': p,
                        'system': system_latest,
                        'system_history': system_history,
                        'services': services_latest,
                        'services_history': services_history,
                        'rpms': rpms_latest,
                        'rpms_history': rpms_history,
                        'interfaces': interfaces_latest,
                        'interfaces_history': interfaces_history,
                        'interfaces_added': interfaces_added_ids}
    return render_to_response('devices/detail.html', template_context,
        context_instance=RequestContext(request))


def results(request, device_slug):
    p = get_object_or_404(Device, hostname=device_slug)
    return render_to_response('devices/results.html', {'device': p},
        context_instance=RequestContext(request))


def vote(request, device_slug):
    '''
    p = get_object_or_404(Device, hostname=device_slug)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the device voting form.
        return render_to_response('devices/detail.html', {
            'device': p,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('secinv.devices.views.results',
            args=(p.id,)))
    '''
    pass


def search(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        form = DeviceSearchForm(request.GET)
        if form.is_valid():
            results = form.get_result_queryset()
    else:
        form = DeviceSearchForm()

    template_context = {'form': form,
                        'results': results,
                        'query': query}
    return render_to_response('devices/search.html', template_context,
        context_instance=RequestContext(request))

'''
def search(request):
    query = request.GET.get('q', '')
    if query:
        qset = (
            Q(sys_ip__icontains=query) |
            Q(hostname__icontains=query)
        )
        results = Device.objects.filter(qset).distinct()
    else:
        results = []
    template_context = {'results': results,
                        'query': query}
    return render_to_response('devices/search.html', template_context,
        context_instance=RequestContext(request))
'''
