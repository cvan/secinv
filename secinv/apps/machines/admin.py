#from .models import Machine
from .models import *
from django.contrib import admin

#admin.site.register(Machine)

#class ChoiceInline(admin.StackedInline):

class SystemInline(admin.TabularInline):
    model = System

class InterfaceInline(admin.TabularInline):
    model = Interface
    extra = 2

class ServicesInline(admin.TabularInline):
    model = Services

class SSHConfigInline(admin.TabularInline):
    model = SSHConfig

class RPMSInline(admin.TabularInline):
    model = RPMs

class IPTablesInline(admin.TabularInline):
    model = IPTables

class ApacheConfigInline(admin.TabularInline):
    model = ApacheConfig

class MachineAdmin(admin.ModelAdmin):
    fieldsets = [(None,               {'fields': ['sys_ip',
                                                  'hostname', 'ext_ip']}),
                 ('Date information', {'fields': ['date_modified',
                                                  'date_scanned'],
                                       'classes': 'collapse'}),]

    inlines = [SystemInline, InterfaceInline, ServicesInline, 
               SSHConfigInline, RPMSInline, IPTablesInline, ApacheConfigInline]

    list_display = ('sys_ip', 'hostname', 'ext_ip',
                    'date_added', 'date_modified', 'date_scanned')
    list_filter = ['hostname']
    search_fields = ['sys_ip', 'hostname', 'ext_ip',
                     'system__kernel_rel', 'system__rh_rel', 'system__nfs',
                     'interface__i_name', 'interface__i_ip',
                     'interface__i_mac', 'interface__i_mask',
                     'services__k_processes', 'services__v_ports',
                     'sshconfig__k_parameters', 'sshconfig__v_values',
                     'rpms__v_rpms', 'iptables__body',
                     'apacheconfig__body']
    date_hierarchy = 'date_added'

admin.site.register(Machine, MachineAdmin)


class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'active')

admin.site.register(AuthToken, AuthTokenAdmin)

