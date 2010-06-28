from .models import *
from django.contrib import admin
from django import forms


class ClassificationForm(forms.ModelForm):
    classification = forms.MultipleChoiceField(choices=CLASSIFICATION_CHOICES,
                                         widget=forms.CheckboxSelectMultiple(), required=False)
    #MultipleChoiceField
    
    '''
    def clean_classification(self):
        return self.cleaned_data['classification']
    '''

    def clean(self):
        return self.cleaned_data


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('machine', 'name', 'url', 'date_added', 'date_modified')
    list_filter = ['name']
    search_fields = ['machine', 'overview', 'contacts', 'url', 'source_code_path',
                     'bugzilla_product', 'bugzilla_component',
                     'visibility']
    date_hierarchy = 'date_added'
    radio_fields = {'visibility': admin.VERTICAL}

admin.site.register(Application, ApplicationAdmin)


class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('application', 'reviewer', 'date_added', 'date_modified')
    list_filter = ['application']
    search_fields = ['application', 'reviewer', 'notes', 'bugs', 'classification']
    date_hierarchy = 'date_added'
    form = ClassificationForm

admin.site.register(Assessment, AssessmentAdmin)



