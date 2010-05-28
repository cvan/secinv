from secinv.machines.models import Machine
from secinv.machines.models import *
from django.contrib import admin

#admin.site.register(Machine)

#class ChoiceInline(admin.StackedInline):
'''
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
'''

class InterfaceInline(admin.TabularInline):
    model = Interface
    extra = 2
    #fields = ('i_name', 'i_ip', 'i_mac', 'i_mask')
    #list_display

class SystemInline(admin.TabularInline):
    model = System

class ServicesInline(admin.TabularInline):
    model = Services

class RPMSInline(admin.TabularInline):
    model = RPMs

class MachineAdmin(admin.ModelAdmin):
    #fields = ['sys_ip', 'hostname', 'ext_ip']
    fieldsets = [(None,               {'fields': ['sys_ip',
                                                  'hostname', 'ext_ip']}),
                 ('Date information', {'fields': ['date_modified',
                                                  'date_scanned'],
                                       'classes': 'collapse'}),]
    inlines = [SystemInline, ServicesInline, RPMSInline, InterfaceInline]

    list_display = ('sys_ip', 'hostname', 'ext_ip',
                    'date_added', 'date_modified', 'date_scanned')
    list_filter = ['hostname']
    search_fields = ['sys_ip', 'hostname', 'ext_ip']
    date_hierarchy = 'date_added'

admin.site.register(Machine, MachineAdmin)


