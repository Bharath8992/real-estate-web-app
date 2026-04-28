from django import forms
from crispy_forms.helper import FormHelper
from django.shortcuts import redirect
from crispy_forms.layout import Layout, Fieldset, ButtonHolder
from crispy_forms.helper import *
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from squarebox import models


class PropertyCreateUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', None)
        super(PropertyCreateUpdateForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].label = str(self.fields[field_name].label).upper()
            self.fields[field_name].widget.attrs['class'] = "form-control form-control-solid"

            if field_name in ["lat", "lng"]:
                self.fields[field_name].widget = HiddenInput()

        if mode == "edit":
            instance = kwargs.get('instance', None)
        save_button_name = "SAVE"

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                Row(
                    Column(Field('listing_type'), css_class='col-12'),
                    Column(Field('title'), css_class='col-12'),
                    Column(Field('address'), css_class='col-12'),
                    Column(Field('city'), css_class='col-12'),
                    Column(Field('state'), css_class='col-12'),
                    Column(Field('zipcode'), css_class='col-12'),
                    Column(Field('description'), css_class='col-12'),
                    Column(Field('price'), css_class='col-12'),
                    Column(Field('bedrooms'), css_class='col-12'),
                    Column(Field('bathrooms'), css_class='col-12'),
                    Column(Field('sqft'), css_class='col-12'),
                    Column(Field('garage'), css_class='col-12'),
                    Column(Field('is_published'), css_class='col-12'),
                    Column(Field('is_hot_selling'), css_class='col-12'),
                    Column(Field('main_image'), css_class='col-12'),
                    Column(Field('property_type'), css_class='col-12'),
                      #apartment
                    Column(Field('floor_number'), css_class='col-12'),
                    Column(Field('total_floors'), css_class='col-12'),
                    Column(Field('building_age'), css_class='col-12'),
                    Column(Field('maintenance_charges'), css_class='col-12'),
                    #villa
                    Column(Field('plot_area'), css_class='col-12'),
                    Column(Field('builtup_area'), css_class='col-12'),
                    Column(Field('facing_direction'), css_class='col-12'),
                    Column(Field('garden_area'), css_class='col-12'),
                  # Land specific fields
                    Column(Field('plot_length'), css_class='col-12'),
                    Column(Field('plot_width'), css_class='col-12'),
                    Column(Field('water_availability'), css_class='col-12'),
                    Column(Field('soil_type'), css_class='col-12'),
                  # Commercial specific fields
                    Column(Field('commercial_type'), css_class='col-12'),
                    Column(Field('floor_height'), css_class='col-12'),
                    Column(Field('loading_capacity'), css_class='col-12'),
                    Column(Field('parking_capacity'), css_class='col-12'),
 
     # Office specific fields
                    Column(Field('office_type'), css_class='col-12'),
                    Column(Field('furnishing_type'), css_class='col-12'),
                    Column(Field('conference_rooms'), css_class='col-12'),
                    Column(Field('reception_area'), css_class='col-12'),
    # Townhouse specific fields
                    Column(Field('units_in_complex'), css_class='col-12'),
                    Column(Field('corner_unit'), css_class='col-12'),
                    Column(Field('end_unit'), css_class='col-12'),
                    Column(Field('hoa_fee'), css_class='col-12'),

                ),
            ),
            ButtonHolder(
                Div(
                    HTML('<a class="btn btn-secondary me-3" href="javascript:void();" onclick="history.back()">CANCEL</a>'),
                    Submit('create_button', save_button_name, css_class='btn btn-lg btn-primary'),
                    css_class="d-flex text-right justify-content-end pt-10 col-12"
                ),
                css_class="row col-12 pe-5",
            )
        )

    class Meta:
        model = models.Property
        exclude = [ 'user', 'created_on', 'updated_on', 'created_by', 'updated_by', 'datamode']

class PropertyTypeCreateUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', None)
        super(PropertyTypeCreateUpdateForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].label = str(self.fields[field_name].label).upper()
            self.fields[field_name].widget.attrs['class'] = "form-control form-control-solid"
        
        if mode == "edit":
            instance = kwargs.get('instance', None)
        save_button_name = "SAVE"

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                Row(Column(Field('name')), css_class='col-12'),
            ),
            ButtonHolder(
                Div(
                    HTML('<a class="btn btn-lg btn-secondary me-3" href="javascript:void();" onclick="history.back()">CANCEL</a>'),
                    Submit('create_button', save_button_name, css_class='btn btn-lg btn-primary'),
                    css_class="d-flex text-right justify-content-end pt-10 col-12"
                ),
                css_class="row col-12 pe-5",
            )
        )

    class Meta:
        model = models.PropertyType
        exclude = ['created_on', 'updated_on', 'created_by', 'updated_by', 'datamode']
        help_texts = {
            'name': 'Enter the type of property (e.g., Apartment, Villa, Plot).',
        }



class LeadCreateUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', None)
        super(LeadCreateUpdateForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].label = str(self.fields[field_name].label).upper()
            self.fields[field_name].widget.attrs['class'] = "form-control form-control-solid"
        
        if mode == "edit":
            instance = kwargs.get('instance', None)
        save_button_name = "SAVE"

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                Row(Column(Field('property')), css_class='col-12'),
                Row(Column(Field('name')), css_class='col-12'),
                Row(Column(Field('email')), css_class='col-12'),
                Row(Column(Field('phone')), css_class='col-12'),
                Row(Column(Field('message')), css_class='col-12'),
                Row(Column(Field('date_submitted')), css_class='col-12'),
                Row(Column(Field('location')), css_class='col-12'),
                
            ),
            ButtonHolder(
                Div(
                    HTML('<a class="btn btn-lg btn-secondary me-3" href="javascript:void();" onclick="history.back()">CANCEL</a>'),
                    Submit('create_button', save_button_name, css_class='btn btn-lg btn-primary'),
                    css_class="d-flex text-right justify-content-end pt-10 col-12"
                ),
                css_class="row col-12 pe-5",
            )
        )

    class Meta:
        model = models.Lead
        exclude = ['created_on', 'updated_on', 'created_by', 'updated_by', 'datamode']
      
class PropertyImageCreateUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', None)
        super(PropertyImageCreateUpdateForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].label = str(self.fields[field_name].label).upper()
            self.fields[field_name].widget.attrs['class'] = "form-control form-control-solid"
        
        if mode == "edit":
            instance = kwargs.get('instance', None)
        save_button_name = "SAVE"

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                Row(Column(Field('property')), css_class='col-12'),
                Row(Column(Field('image')), css_class='col-12'),
            ),
            ButtonHolder(
                Div(
                    HTML('<a class="btn btn-lg btn-secondary me-3" href="javascript:void();" onclick="history.back()">CANCEL</a>'),
                    Submit('create_button', save_button_name, css_class='btn btn-lg btn-primary'),
                    css_class="d-flex text-right justify-content-end pt-10 col-12"
                ),
                css_class="row col-12 pe-5",
            )
        )

    class Meta:
        model = models.PropertyImage
        exclude = ['created_on', 'updated_on', 'created_by', 'updated_by', 'datamode']
        help_texts = {
            'image': 'Enter the type of property (e.g., Apartment, Villa, Plot).',
        }


class MaintenanceCreateUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', None)
        super(MaintenanceCreateUpdateForm, self).__init__(*args, **kwargs)

        # Uppercase labels and bootstrap classes
        for field_name in self.fields:
            self.fields[field_name].label = str(self.fields[field_name].label).upper()
            self.fields[field_name].widget.attrs['class'] = "form-control form-control-solid"

        if mode == "edit":
            instance = kwargs.get('instance', None)

        save_button_name = "SAVE"

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                # Row(Column('property', css_class='col-12 mb-2')),
                Row(Column('description', css_class='col-12 mb-2')),
                Row(Column('urgency', css_class='col-6 mb-2'), Column('preferred_date', css_class='col-6 mb-2')),
                Row(Column('attachment', css_class='col-12 mb-2')),
                Row(Column('status', css_class='col-6 mb-2') ),
            ),
            ButtonHolder(
                Div(
                    HTML('<a class="btn btn-lg btn-secondary me-3" href="javascript:void();" onclick="history.back()">CANCEL</a>'),
                    Submit('create_button', save_button_name, css_class='btn btn-lg btn-primary'),
                    css_class="d-flex text-right justify-content-end pt-10 col-12"
                ),
                css_class="row col-12 pe-5",
            )
        )

    class Meta:
        model = models.MaintenanceRequest
        exclude = ['created_on', 'updated_on', 'created_by', 'updated_by', 'datamode']
        widgets = {
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'description': 'Describe the maintenance issue in detail.',
            'attachment': 'Optional: Upload images or documents related to the issue.',
            'urgency': 'Select the urgency level for this maintenance request.',
            'status': 'Current status of the request.',
            'assigned_to': 'Assign an agent to handle this request.',
        }