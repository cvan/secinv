from django.conf import settings
from apps.machines.views import (get_all_machines, get_all_domains,
                                 get_all_directives, get_all_items)

def global_settings(request):
    query = request.GET.get('q', '')

    return {'query': query,
            'all_machines_hn': get_all_machines('hostname'),
            'all_machines_ip': get_all_machines('sys_ip'),
            'all_domains': get_all_domains(),
            'all_directives': get_all_directives(),
            'all_php_items': get_all_items('phpconfig'),
            'all_mysql_items': get_all_items('mysqlconfig'),
            'all_ssh_items': get_all_items('sshconfig'),}

