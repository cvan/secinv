from .models import (Machine, Services, System, RPMs, Interface, SSHConfig,
                     IPTables, ApacheConfig, PHPConfig, MySQLConfig, 
                     AuthToken)
from django.contrib import admin
from django.conf.urls.defaults import patterns, url

from .views import add_multiple_machines

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
    model = Machine
    fieldsets = [(None,               {'fields': ['sys_ip',
                                                  'hostname', 'ext_ip',
                                                  'token']}),
                 ('Date information', {'fields': ['date_modified',
                                                  'date_scanned'],
                                       'classes': 'collapse'}),]

    inlines = [SystemInline, InterfaceInline, ServicesInline, 
               SSHConfigInline, RPMSInline, IPTablesInline,
               ApacheConfigInline]

    list_display = ('sys_ip', 'hostname', 'ext_ip',
                    'date_added', 'date_modified', 'date_scanned')
    list_filter = ['hostname']
    search_fields = ['sys_ip', 'hostname', 'ext_ip',
                     'system__kernel_rel', 'system__rh_rel', 'system__nfs',
                     'system__ip_fwd', 'system__iptables',
                     'services__k_processes', 'services__v_ports',
                     'rpms__v_rpms',
                     'interface__i_name', 'interface__i_ip',
                     'interface__i_mac', 'interface__i_mask',
                     'sshconfig__body', 'sshconfig__filename',
                     'apacheconfig__body', 'apacheconfig__filename',
                     'iptables__body',
                     'phpconfig__body', 'phpconfig__filename',
                     'mysqlconfig__body', 'mysqlconfig__filename']

    date_hierarchy = 'date_added'

    def get_urls(self):
        urls = super(MachineAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^add_multiple_machines/$',
                self.admin_site.admin_view(add_multiple_machines),
                name='add_multiple_machines'),
        )
        return my_urls + urls

admin.site.register(Machine, MachineAdmin)


class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'active')

admin.site.register(AuthToken, AuthTokenAdmin)
