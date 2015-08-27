from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

from manager import models
from core import models as core_models

from pprint import pprint

class GroupForm(forms.ModelForm):

    class Meta:
        model = models.Group
        exclude = ()

class EditKey(forms.Form):

	def __init__(self, *args, **kwargs):
		key_type = kwargs.pop('key_type', None)
		value = kwargs.pop('value', None)
		super(EditKey, self).__init__(*args, **kwargs)

		print key_type, value
		if key_type == 'rich_text':
			self.fields['value'].widget = SummernoteWidget()
		elif key_type == 'boolean':
			self.fields['value'].widget = forms.CheckboxInput()
		elif key_type == 'integer':
			self.fields['value'].widget = forms.TextInput(attrs={'type': 'number'})
		elif key_type == 'file' or key_type == 'journalthumb':
			self.fields['value'].widget = forms.FileInput()
		elif key_type == 'text':
			self.fields['value'].widget = forms.Textarea()
		else:
			self.fields['value'].widget.attrs['size'] = '100%'

		self.fields['value'].initial = value

	value = forms.CharField(label='')

	def clean(self):
		cleaned_data = self.cleaned_data

class ProposalForm(forms.Form):

	proposal_forms =[(proposal_form.pk, proposal_form) for proposal_form in core_models.ProposalForm.objects.all()]
	selection = forms.ChoiceField(widget=forms.Select, choices=proposal_forms)

class DefaultForm(forms.Form):

	title = forms.CharField(widget=forms.TextInput, required=True)
	subtitle = forms.CharField(widget=forms.TextInput, required=True)
	author = forms.CharField(widget=forms.TextInput, required=True)

def render_choices(choices):
	c_split = choices.split('|')
	return [(choice.capitalize(), choice) for choice in c_split]

class GeneratedForm(forms.Form):

	def __init__(self, *args, **kwargs):

		form_obj = kwargs.pop('form', None)
		super(GeneratedForm, self).__init__(*args, **kwargs)
		relations = core_models.ProposalFormElementsRelationship.objects.filter(form=form_obj)
		for relation in relations:

			if relation.element.field_type == 'text':
				self.fields[relation.element.name] = forms.CharField(widget=forms.TextInput(attrs={'div_class':relation.width}), required=relation.element.required)
			elif relation.element.field_type == 'textarea':
				self.fields[relation.element.name] = forms.CharField(widget=forms.Textarea, required=relation.element.required)
			elif relation.element.field_type == 'date':
				self.fields[relation.element.name] = forms.CharField(widget=forms.DateInput(attrs={'class':'datepicker', 'div_class':relation.element_class}), required=relation.element.required)
			elif relation.element.field_type == 'upload':
				self.fields[relation.element.name] = forms.FileField(required=relation.element.required)
			elif relation.element.field_type == 'select':
				if relation.element.name == 'Series':
					choices = series_list
				else:
					choices = render_choices(relation.element.choices)
				self.fields[relation.element.name] = forms.ChoiceField(widget=forms.Select(attrs={'div_class':relation.width}), choices=choices, required=relation.element.required)
			elif relation.element.field_type == 'email':
				self.fields[relation.element.name] = forms.EmailField(widget=forms.TextInput(attrs={'div_class':relation.width}), required=relation.element.required)
			elif relation.element.field_type == 'check':
				self.fields[relation.element.name] = forms.BooleanField(widget=forms.CheckboxInput(attrs={'is_checkbox':True}), required=relation.element.required)
			self.fields[relation.element.name].help_text = relation.help_text


