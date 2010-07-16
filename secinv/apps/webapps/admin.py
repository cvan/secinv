from .models import *
from django.contrib import admin
from django import forms

CLASSIFICATION_CHOICES = (
    ('a', 'code review'),
    ('b', 'app penetration'),
    ('c', 'risk assessment'),
)

class ClassificationForm(forms.ModelForm):
    class Meta:
        model = Assessment

    classification = forms.MultipleChoiceField(choices=CLASSIFICATION_CHOICES,
        widget=forms.CheckboxSelectMultiple(), required=False)
    '''
    def clean_classification(self):
        return self.cleaned_data['classification']
    '''

    def clean(self):
        return self.cleaned_data

    #def clean_classification(self):
    #    return self.cleaned_data['classification']

    #def clean(self):
    #    return self


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('machine', 'name', 'url', 'date_added', 'date_modified')
    list_filter = ['name']
    search_fields = ['machine', 'overview', 'contacts', 'url',
                     'source_code_url', 'source_code_path',
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
    #form = ClassificationForm
    model = Assessment

    #def save_model(self, request, model, form, change):
    #    model.save()

admin.site.register(Assessment, AssessmentAdmin)


