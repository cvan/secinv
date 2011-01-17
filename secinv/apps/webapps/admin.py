from django.contrib import admin
from django import forms

from .models import *


CLASSIFICATION_CHOICES = (
    (u'a', 'code review'),
    (u'b', 'app penetration'),
    (u'c', 'risk assessment'),
)

class ClassificationForm(forms.ModelForm):
    class Meta:
        model = Assessment

    classification = forms.MultipleChoiceField(choices=CLASSIFICATION_CHOICES,
        widget=forms.CheckboxSelectMultiple(), required=False)

    def clean_classification(self):
        classification = self.data.getlist('classification')
        return classification


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'date_added', 'date_modified')
    list_filter = ['name']
    search_fields = ['machine', 'machine__hostname', 'machine__sys_ip',
                     'overview', 'contacts', 'url',
                     'source_code_url', 'source_code_path',
                     'bugzilla_product', 'bugzilla_component',
                     'visibility']
    date_hierarchy = 'date_added'
    radio_fields = {'visibility': admin.VERTICAL}

admin.site.register(Application, ApplicationAdmin)


class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('application', 'reviewer', 'date_added', 'date_modified')
    list_filter = ['application']
    search_fields = ['application', 'reviewer', 'notes', 'bugs',
                     'classification']
    date_hierarchy = 'date_added'
    form = ClassificationForm
    model = Assessment

admin.site.register(Assessment, AssessmentAdmin)

