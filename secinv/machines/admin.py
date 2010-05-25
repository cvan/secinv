from secinv.machines.models import Machine
from secinv.machines.models import Choice
from django.contrib import admin

#admin.site.register(Machine)

#class ChoiceInline(admin.StackedInline):
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class MachineAdmin(admin.ModelAdmin):
    #fields = ['pub_date', 'question']
    fieldsets = [(None,               {'fields': ['question']}),
                 ('Date information', {'fields': ['pub_date'],
                                       'classes': 'collapse'}),]
    inlines = [ChoiceInline]

    list_display = ('question', 'pub_date', 'was_published_today')
    list_filter = ['pub_date']
    search_fields = ['question']
    date_hierarchy = 'pub_date'
    

admin.site.register(Machine, MachineAdmin)

#admin.site.register(Choice)



