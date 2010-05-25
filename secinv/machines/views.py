from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from secinv.machines.models import Machine
#from django.http import HttpResponse

def index(request):
    latest_machine_list = Machine.objects.all().order_by('-pub_date')[:5]
    return render_to_response('machines/index.html', {'latest_machine_list': latest_machine_list},
        context_instance=RequestContext(request))

def detail(request, machine_id):
    #p = Machine.objects.get(pk=machine_id)
    p = get_object_or_404(Machine, pk=machine_id)
    return render_to_response('machines/detail.html', {'machine': p})

def results(request, machine_id):
    p = get_object_or_404(Machine, pk=machine_id)
    return render_to_response('machines/results.html', {'machine': p})

def vote(request, machine_id):
    p = get_object_or_404(Machine, pk=machine_id)
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

