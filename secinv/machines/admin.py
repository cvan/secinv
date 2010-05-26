from secinv.machines.models import Machine
from secinv.machines.models import Choice, Interface, System, Services, RPMs
from django.contrib import admin

#admin.site.register(Machine)

#class ChoiceInline(admin.StackedInline):
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

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
    #fields = ['pub_date', 'question']
    fieldsets = [(None,               {'fields': ['question', 'sys_ip',
                                                  'hostname', 'ext_ip']}),
                 ('Date information', {'fields': ['pub_date', 'date_updated'],
                                       'classes': 'collapse'}),]
    inlines = [ChoiceInline, SystemInline, ServicesInline, RPMSInline,
               InterfaceInline]

    list_display = ('sys_ip', 'hostname', 'ext_ip', 'question', 'pub_date',
                    'date_added', 'date_updated', 'date_scanned',
                    'was_published_today')
    list_filter = ['pub_date']
    search_fields = ['question', 'sys_ip', 'hostname', 'ext_ip']
    date_hierarchy = 'pub_date'


admin.site.register(Machine, MachineAdmin)


