import sys
from phonenumber_field.phonenumber import PhoneNumber
from django.urls import reverse
from django.forms.models import model_to_dict
from config import app_utils
from config import app_logger
from mck_auth import api as auth_api
from django.utils.dateparse import parse_datetime
from squarebox.models import *
from django.core.mail import send_mail, EmailMessage
from django.conf import settings

log_name = "app"
logger = app_logger.createLogger(log_name)



# Support Page Content
@app_logger.functionlogs(log=log_name)
def property_load_data(request, table_data):
    result = False
    success_msg = "Success"
    error_msg = 'Internal Server Error'
    fResult = list()
    try:
        queryset = Property.objects.exclude(datamode='D').order_by('-updated_on')
        qs, total_records, total_display_records = app_utils.method_for_datatable_operations(
            request, queryset)

        final_data = list()
        for qs_instance in qs:
            qs_data = model_to_dict(qs_instance)
            data = list()
            edit_url = reverse('squarebox:property_update', args=[qs_data['id']])

            for column in table_data['columns']:
                if column['column_name'] == "datamode":
                    if qs_instance.datamode == "A":
                        data.append('<div class="text-success">'+qs_instance.get_datamode_display()+'</div>')
                        data.append('<div class="text-end"><a href="'+edit_url+'" class="text-primary pe-2 ps-2">Edit</a> | <a href="javascript:void()" class="text-danger ps-2" onclick="delete_object('+str(qs_data['id'])+')">Inactivate</a></div>')
                    else:
                        data.append('<div class="text-danger">'+qs_instance.get_datamode_display()+'</div>')
                        data.append('<div class="text-end"><a href="'+edit_url+'" class="text-primary pe-2 ps-2">Edit</a> | <a href="javascript:void()" class="text-success ps-2" onclick="delete_object('+str(qs_data['id'])+')">Activate</a></div>')
                # elif column['column_name'] == "property_type":
                #     data.append(qs_instance.name)
                else:
                    if isinstance(qs_data.get(column['column_name']), PhoneNumber):
                        data.append(qs_data.get(column['column_name']).national_number)
                    elif isinstance(qs_data.get(column['column_name']), models.ImageField):
                        pass
                    else:
                        data.append(qs_data.get(column['column_name'], "-"))
            final_data.append(data)
        fResult = app_utils.final_dict(request, total_records, total_display_records, final_data)

        result, msg = True, success_msg
    except Exception as e:
        result, msg = False, error_msg
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
    return result, msg, fResult


@app_logger.functionlogs(log=log_name)
def property_retrieve_data(request, id):
    result = False
    success_msg = "Success"
    error_msg = 'Internal Server Error'
    data = dict()
    try:
        property = Property.objects.filter(id=id).first()
        if property:
            data['property'] = property
            result, msg = True, success_msg
        else:
            result, msg, data = True, success_msg, data
    except Exception as e:
        result, msg = False, error_msg
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
    return result, msg, data

def to_int(value, default=None):
    try:
        return int(value) if value not in [None, '', 'null'] else default
    except (ValueError, TypeError):
        return default

def to_float(value, default=None):
    try:
        return float(value) if value not in [None, '', 'null'] else default
    except (ValueError, TypeError):
        return default

def to_bool(value):
    return str(value).lower() in ['true', '1', 'yes']


@app_logger.functionlogs(log=log_name)
def property_create_update(request, id=None, mode=None):
    result = False
    success_msg = "Success"
    error_msg = 'Internal Server Error'
    data = dict()

    try:
        accountuser = auth_api.get_request_accountuser(request)
        pDict = request.POST

        if mode == 'edit' and id:
            obj = Property.objects.filter(id=id, datamode='A').first()
            if not obj:
                return False, "Property not found", data
        else:
            obj = Property()
            obj.created_by = str(accountuser.id)   # store as string for consistency

        # ----- THE FIX -----
        # Always attach the Django auth user so the FK is populated.
        if request.user.is_authenticated:
            obj.user = request.user
        # -------------------

        # Basic info
        obj.listing_type = pDict.get('listing_type')
        obj.title = pDict.get('title')
        obj.address = pDict.get('address')
        obj.city = pDict.get('city')
        obj.state = pDict.get('state')
        obj.zipcode = pDict.get('zipcode')
        obj.description = pDict.get('description')
        obj.property_type = PropertyType.objects.filter(id=pDict.get("property_type")).first()

        # Numbers
        obj.price = to_int(pDict.get('price'))
        obj.bedrooms = to_int(pDict.get('bedrooms'))
        obj.bathrooms = to_int(pDict.get('bathrooms'))
        obj.sqft = to_int(pDict.get('sqft'))
        obj.garage = to_int(pDict.get('garage'))

        obj.floor_number = to_int(pDict.get('floor_number'))
        obj.total_floors = to_int(pDict.get('total_floors'))
        obj.building_age = to_int(pDict.get('building_age'))
        obj.maintenance_charges = to_float(pDict.get('maintenance_charges'))

        obj.plot_area = to_float(pDict.get('plot_area'))
        obj.builtup_area = to_float(pDict.get('builtup_area'))
        obj.facing_direction = pDict.get('facing_direction')
        obj.garden_area = to_float(pDict.get('garden_area'))

        obj.plot_length = to_float(pDict.get('plot_length'))
        obj.plot_width = to_float(pDict.get('plot_width'))
        obj.water_availability = pDict.get('water_availability')
        obj.soil_type = pDict.get('soil_type')

        obj.commercial_type = pDict.get('commercial_type')
        obj.floor_height = to_float(pDict.get('floor_height'))
        obj.loading_capacity = to_float(pDict.get('loading_capacity'))
        obj.parking_capacity = to_int(pDict.get('parking_capacity'))

        obj.office_type = pDict.get('office_type')
        obj.furnishing_type = pDict.get('furnishing_type')
        obj.conference_rooms = to_int(pDict.get('conference_rooms'))
        obj.reception_area = pDict.get('reception_area')

        obj.units_in_complex = to_int(pDict.get('units_in_complex'))
        obj.corner_unit = pDict.get('corner_unit')
        obj.end_unit = pDict.get('end_unit')
        obj.hoa_fee = to_float(pDict.get('hoa_fee'))

        # Booleans
        obj.is_published = to_bool(pDict.get('is_published'))
        obj.is_hot_selling = to_bool(pDict.get('is_hot_selling'))

        # Dates
        list_date_str = pDict.get('list_date')
        obj.list_date = parse_datetime(list_date_str) if list_date_str else None

        # Image
        if request.FILES.get('main_image'):
            obj.main_image = request.FILES.get('main_image')

        obj.updated_by = str(accountuser.id)
        obj.save()

        data['property'] = obj
        result, msg = True, success_msg

    except Exception as e:
        result, msg = False, error_msg
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error(f'Error at line {exc_traceback.tb_lineno}: {e}')

    return result, msg, data
    

@app_logger.functionlogs(log=log_name)
def property_update_status(request, id):
    result = False
    message = 'Error'
    try:
        accountuser = auth_api.get_request_accountuser(request)
        obj = Property.objects.filter(id=id).first()
        if obj:
            obj.updated_by = accountuser.id
            if obj.datamode == "I":
                obj.datamode = "A"
            else:
                obj.datamode = "I"
            obj.save()

        result = True
        message = 'Sucesss'
    except Exception as e:
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
    return result, message




@app_logger.functionlogs(log=log_name)
def property_type_load_data(request, table_data):
    result = False
    success_msg = "Success"
    error_msg = 'Internal Server Error'
    fResult = list()
    try:
        queryset = PropertyType.objects.exclude(datamode='D').order_by('-updated_on')
        qs, total_records, total_display_records = app_utils.method_for_datatable_operations(
            request, queryset)

        final_data = list()
        for qs_instance in qs:
            qs_data = model_to_dict(qs_instance)
            data = list()
            edit_url = reverse('squarebox:property_type_update', args=[qs_data['id']])

            for column in table_data['columns']:
                if column['column_name'] == "datamode":
                    data.append('<div class="text-success">'+qs_instance.get_datamode_display()+'</div>')
                    data.append('<div class="text-end"><a href="'+edit_url+'" class="text-primary pe-2 ps-2">Edit</a>')
                    if qs_instance.datamode == "A":
                        data.append('<div class="text-success">'+qs_instance.get_datamode_display()+'</div>')
                        data.append('<div class="text-end"><a href="'+edit_url+'" class="text-primary pe-2 ps-2">Edit</a> | <a href="javascript:void()" class="text-danger ps-2" onclick="delete_object('+str(qs_data['id'])+')">Inactivate</a></div>')
                    else:
                        data.append('<div class="text-danger">'+qs_instance.get_datamode_display()+'</div>')
                        data.append('<div class="text-end"><a href="'+edit_url+'" class="text-primary pe-2 ps-2">Edit</a> | <a href="javascript:void()" class="text-success ps-2" onclick="delete_object('+str(qs_data['id'])+')">Activate</a></div>')
                else:
                    if isinstance(qs_data.get(column['column_name']), PhoneNumber):
                        data.append(qs_data.get(column['column_name']).national_number)
                    elif isinstance(qs_data.get(column['column_name']), models.ImageField):
                        pass
                    else:
                        data.append(qs_data.get(column['column_name'], "-"))
            final_data.append(data)
        fResult = app_utils.final_dict(request, total_records, total_display_records, final_data)

        result, msg = True, success_msg
    except Exception as e:
        result, msg = False, error_msg
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
    return result, msg, fResult


@app_logger.functionlogs(log=log_name)
def property_type_retrieve_data(request, id):
    result = False
    success_msg = "Success"
    error_msg = 'Internal Server Error'
    data = dict()
    try:
        property_type = PropertyType.objects.filter(id=id).first()
        if property_type:
            data['property_type'] = property_type
            result, msg = True, success_msg
        else:
            result, msg, data = True, success_msg, data
    except Exception as e:
        result, msg = False, error_msg
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
    return result, msg, data


@app_logger.functionlogs(log=log_name)
def property_type_create_update(request, id=None, mode=None):
    result = False
    success_msg = "Success"
    error_msg = 'Internal Server Error'
    data = dict()
    try:
        accountuser = auth_api.get_request_accountuser(request)
        pDict = request.POST
        if mode == 'edit' and id:
            obj = PropertyType.objects.filter(id=id).first()
        else:
            obj = PropertyType()
            obj.created_by = accountuser.id
            
        obj.name = pDict.get('name')

        obj.updated_by = accountuser.id
        obj.save()

        data['property_type'] = obj
        
        result, msg = True, success_msg
    except Exception as e:
        result, msg = False, error_msg
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
    return result, msg, data


@app_logger.functionlogs(log=log_name)
def property_type_update_status(request, id):
    result = False
    message = 'Error'
    try:
        accountuser = auth_api.get_request_accountuser(request)
        obj = PropertyType.objects.filter(id=id).first()
        if obj:
            obj.updated_by = accountuser.id
            if obj.datamode == "I":
                obj.datamode = "A"
            else:
                obj.datamode = "I"
            obj.save()

        result = True
        message = 'Sucesss'
    except Exception as e:
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
    return result, message




@app_logger.functionlogs(log=log_name)
def lead_load_data(request, table_data):
    result = False
    success_msg = "Success"
    error_msg = 'Internal Server Error'
    fResult = list()
    try:
        queryset = Lead.objects.exclude(datamode='D').order_by('-updated_on')
        qs, total_records, total_display_records = app_utils.method_for_datatable_operations(
            request, queryset)

        final_data = list()
        for qs_instance in qs:
            qs_data = model_to_dict(qs_instance)
            data = list()
            edit_url = reverse('squarebox:lead_update', args=[qs_data['id']])

            for column in table_data['columns']:
                if column['column_name'] == "datamode":
                    data.append('<div class="text-success">'+qs_instance.get_datamode_display()+'</div>')
                    data.append('<div class="text-end"><a href="'+edit_url+'" class="text-primary pe-2 ps-2">Edit</a>')
                    if qs_instance.datamode == "A":
                        data.append('<div class="text-success">'+qs_instance.get_datamode_display()+'</div>')
                        data.append('<div class="text-end"><a href="'+edit_url+'" class="text-primary pe-2 ps-2">Edit</a> | <a href="javascript:void()" class="text-danger ps-2" onclick="delete_object('+str(qs_data['id'])+')">Inactivate</a></div>')
                    else:
                        data.append('<div class="text-danger">'+qs_instance.get_datamode_display()+'</div>')
                        data.append('<div class="text-end"><a href="'+edit_url+'" class="text-primary pe-2 ps-2">Edit</a> | <a href="javascript:void()" class="text-success ps-2" onclick="delete_object('+str(qs_data['id'])+')">Activate</a></div>')
                elif column['column_name'] == "property":
                    data.append(qs_instance.property.title) 
                else:
                    if isinstance(qs_data.get(column['column_name']), PhoneNumber):
                        data.append(qs_data.get(column['column_name']).national_number)
                    elif isinstance(qs_data.get(column['column_name']), models.ImageField):
                        pass
                    else:
                        data.append(qs_data.get(column['column_name'], "-"))
            final_data.append(data)
        fResult = app_utils.final_dict(request, total_records, total_display_records, final_data)

        result, msg = True, success_msg
    except Exception as e:
        result, msg = False, error_msg
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
    return result, msg, fResult


@app_logger.functionlogs(log=log_name)
def lead_retrieve_data(request, id):
    result = False
    success_msg = "Success"
    error_msg = 'Internal Server Error'
    data = dict()
    try:
        lead = Lead.objects.filter(id=id).first()
        if lead:
            data['lead'] = lead
            result, msg = True, success_msg
        else:
            result, msg, data = True, success_msg, data
    except Exception as e:
        result, msg = False, error_msg
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
    return result, msg, data


@app_logger.functionlogs(log=log_name)
def lead_create_update(request, id=None, mode=None):
    result = False
    success_msg = "Success"
    error_msg = 'Internal Server Error'
    data = dict()
    try:
        accountuser = auth_api.get_request_accountuser(request)
        pDict = request.POST
        if mode == 'edit' and id:
            obj = Lead.objects.filter(id=id).first()
        else:
            obj = Lead()
            obj.created_by = accountuser.id
            
        obj.property = Property.objects.filter(id=pDict.get('property')).first() 
        obj.name = pDict.get('name')
        obj.email = pDict.get('email')
        obj.phone = pDict.get('phone')
        obj.message = pDict.get('message')
        obj.date_submitted = pDict.get('date_submitted')
        obj.location = pDict.get('location')

        obj.updated_by = accountuser.id
        obj.save()

        data['lead'] = obj
        
        result, msg = True, success_msg
    except Exception as e:
        result, msg = False, error_msg
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
    return result, msg, data


@app_logger.functionlogs(log=log_name)
def lead_update_status(request, id):
    result = False
    message = 'Error'
    try:
        accountuser = auth_api.get_request_accountuser(request)
        obj = Lead.objects.filter(id=id).first()
        if obj:
            obj.updated_by = accountuser.id
            if obj.datamode == "I":
                obj.datamode = "A"
            else:
                obj.datamode = "I"
            obj.save()

        result = True
        message = 'Sucesss'
    except Exception as e:
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
    return result, message




@app_logger.functionlogs(log=log_name)
def property_image_load_data(request, table_data):
    result = False
    success_msg = "Success"
    error_msg = 'Internal Server Error'
    fResult = list()
    try:
        queryset = PropertyImage.objects.exclude(datamode='D').order_by('-updated_on')
        qs, total_records, total_display_records = app_utils.method_for_datatable_operations(
            request, queryset)

        final_data = list()
        for qs_instance in qs:
            qs_data = model_to_dict(qs_instance)
            data = list()
            edit_url = reverse('squarebox:property_image_update', args=[qs_data['id']])

            for column in table_data['columns']:
                if column['column_name'] == "datamode":
                    data.append('<div class="text-success">'+qs_instance.get_datamode_display()+'</div>')
                    data.append('<div class="text-end"><a href="'+edit_url+'" class="text-primary pe-2 ps-2">Edit</a>')
                    if qs_instance.datamode == "A":
                        data.append('<div class="text-success">'+qs_instance.get_datamode_display()+'</div>')
                        data.append('<div class="text-end"><a href="'+edit_url+'" class="text-primary pe-2 ps-2">Edit</a> | <a href="javascript:void()" class="text-danger ps-2" onclick="delete_object('+str(qs_data['id'])+')">Inactivate</a></div>')
                    else:
                        data.append('<div class="text-danger">'+qs_instance.get_datamode_display()+'</div>')
                        data.append('<div class="text-end"><a href="'+edit_url+'" class="text-primary pe-2 ps-2">Edit</a> | <a href="javascript:void()" class="text-success ps-2" onclick="delete_object('+str(qs_data['id'])+')">Activate</a></div>')
                elif column['column_name'] == "property":
                    data.append(qs_instance.property.title) 
                else:
                    if isinstance(qs_data.get(column['column_name']), PhoneNumber):
                        data.append(qs_data.get(column['column_name']).national_number)
                    elif isinstance(qs_data.get(column['column_name']), models.ImageField):
                        pass
                    else:
                        data.append(qs_data.get(column['column_name'], "-"))
            final_data.append(data)
        fResult = app_utils.final_dict(request, total_records, total_display_records, final_data)

        result, msg = True, success_msg
    except Exception as e:
        result, msg = False, error_msg
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
    return result, msg, fResult


@app_logger.functionlogs(log=log_name)
def property_image_retrieve_data(request, id):
    result = False
    success_msg = "Success"
    error_msg = 'Internal Server Error'
    data = dict()
    try:
        property_image = PropertyImage.objects.filter(id=id).first()
        if property_image:
            data['property_image'] = property_image
            result, msg = True, success_msg
        else:
            result, msg, data = True, success_msg, data
    except Exception as e:
        result, msg = False, error_msg
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
    return result, msg, data


@app_logger.functionlogs(log=log_name)
def property_image_create_update(request, id=None, mode=None):
    result = False
    success_msg = "Success"
    error_msg = 'Internal Server Error'
    data = dict()
    try:
        accountuser = auth_api.get_request_accountuser(request)
        pDict = request.POST
        if mode == 'edit' and id:
            obj = PropertyImage.objects.filter(id=id).first()
        else:
            obj = PropertyImage()
            obj.created_by = accountuser.id

        
        obj.property = Property.objects.filter(id=pDict.get('property')).first()
        if 'image' in request.FILES:
            obj.image = request.FILES['image']

        obj.updated_by = accountuser.id
        obj.save()

        data['property_image'] = obj
        
        result, msg = True, success_msg
    except Exception as e:
        result, msg = False, error_msg
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
    return result, msg, data


@app_logger.functionlogs(log=log_name)
def property_image_update_status(request, id):
    result = False
    message = 'Error'
    try:
        accountuser = auth_api.get_request_accountuser(request)
        obj = PropertyImage.objects.filter(id=id).first()
        if obj:
            obj.updated_by = accountuser.id
            if obj.datamode == "I":
                obj.datamode = "A"
            else:
                obj.datamode = "I"
            obj.save()

        result = True
        message = 'Sucesss'
    except Exception as e:
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error('Error at %s:%s' % (exc_traceback.tb_lineno, e))
    return result, message


@app_logger.functionlogs(log=log_name)
def maintenance_load_data(request, table_data):
    result = False
    success_msg = "Success"
    error_msg = 'Internal Server Error'
    fResult = list()
    try:
        queryset = MaintenanceRequest.objects.exclude(datamode='D').order_by('-updated_on')
        qs, total_records, total_display_records = app_utils.method_for_datatable_operations(
            request, queryset)

        final_data = list()
        for qs_instance in qs:
            qs_data = model_to_dict(qs_instance)
            data = list()
            edit_url = reverse('squarebox:maintenance_update', args=[qs_data['id']])

            for column in table_data['columns']:
                if column['column_name'] == "datamode":
                    if qs_instance.datamode == "A":
                        data.append(f'<div class="text-success">{qs_instance.get_datamode_display()}</div>')
                        data.append(f'<div class="text-end"><a href="{edit_url}" class="text-primary pe-2 ps-2">Edit</a> | '
                                    f'<a href="javascript:void()" class="text-danger ps-2" onclick="delete_object({qs_data["id"]})">Inactivate</a></div>')
                    else:
                        data.append(f'<div class="text-danger">{qs_instance.get_datamode_display()}</div>')
                        data.append(f'<div class="text-end"><a href="{edit_url}" class="text-primary pe-2 ps-2">Edit</a> | '
                                    f'<a href="javascript:void()" class="text-success ps-2" onclick="delete_object({qs_data["id"]})">Activate</a></div>')
                # elif column['column_name'] == "property":
                #     data.append(qs_instance.property.title if qs_instance.property else "-")
                # elif column['column_name'] == "assigned_to":
                #     data.append(qs_instance.assigned_to.name if qs_instance.assigned_to else "-")
                else:
                    data.append(qs_data.get(column['column_name'], "-"))
            final_data.append(data)
        fResult = app_utils.final_dict(request, total_records, total_display_records, final_data)

        result, msg = True, success_msg
    except Exception as e:
        result, msg = False, error_msg
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error(f'Error at {exc_traceback.tb_lineno}: {e}')
    return result, msg, fResult


@app_logger.functionlogs(log=log_name)
def maintenance_retrieve_data(request, id):
    result = False
    success_msg = "Success"
    error_msg = 'Internal Server Error'
    data = dict()
    try:
        maintenance = MaintenanceRequest.objects.filter(id=id).first()
        if maintenance:
            data['maintenance'] = maintenance
            result, msg = True, success_msg
        else:
            result, msg, data = True, success_msg, data
    except Exception as e:
        result, msg = False, error_msg
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error(f'Error at {exc_traceback.tb_lineno}: {e}')
    return result, msg, data


@app_logger.functionlogs(log=log_name)
def maintenance_create_update(request, id=None, mode=None):
    result = False
    success_msg = "Success"
    error_msg = 'Internal Server Error'
    data = dict()
    try:
        accountuser = auth_api.get_request_accountuser(request)
        pDict = request.POST
        if mode == 'edit' and id:
            obj = MaintenanceRequest.objects.filter(id=id).first()
        else:
            obj = MaintenanceRequest()
            obj.created_by = accountuser.id

        # obj.property = Property.objects.filter(id=pDict.get('property')).first()
        obj.description = pDict.get('description', '')
        obj.urgency = pDict.get('urgency', '')
        obj.preferred_date = pDict.get('preferred_date', None)
        obj.status = pDict.get('status', '')
        # if pDict.get('assigned_to'):
        #     obj.assigned_to = Agent.objects.filter(id=pDict.get('assigned_to')).first()

        if 'attachment' in request.FILES:
            obj.attachment = request.FILES['attachment']

        obj.updated_by = accountuser.id
        obj.save()

        data['maintenance'] = obj
        result, msg = True, success_msg
    except Exception as e:
        result, msg = False, error_msg
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error(f'Error at {exc_traceback.tb_lineno}: {e}')
    return result, msg, data


@app_logger.functionlogs(log=log_name)
def maintenance_update_status(request, id):
    result = False
    message = 'Error'
    try:
        accountuser = auth_api.get_request_accountuser(request)
        obj = MaintenanceRequest.objects.filter(id=id).first()
        if obj:
            obj.updated_by = accountuser.id
            if obj.datamode == "I":
                obj.datamode = "A"
            else:
                obj.datamode = "I"
            obj.save()

        result = True
        message = 'Success'
    except Exception as e:
        exc_type, exc_obj, exc_traceback = sys.exc_info()
        logger.error(f'Error at {exc_traceback.tb_lineno}: {e}')
    return result, message

@app_logger.functionlogs(log=log_name)
def ajax_property_save(request):
    result = False
    message = "Failed to save property"

    def to_int(value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def to_float(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    try:
        pDict = request.POST
        files = request.FILES

        # Save Property
        obj = Property(
            title=pDict.get("title", ""),
            description=pDict.get("description", ""),
            city=pDict.get("city", ""),
            state=pDict.get("state", ""),
            zipcode=pDict.get("zipcode", ""),
            price=to_float(pDict.get("price")),
            bedrooms=to_int(pDict.get("bedrooms")),
            sqft=to_int(pDict.get("sqft")),
            garage=to_int(pDict.get("garage")),
            address=pDict.get("address", ""),

            floor_number=to_int(pDict.get("floor_number")),
            total_floors=to_int(pDict.get("total_floors")),
            building_age=to_int(pDict.get("building_age")),
            maintenance_charges=to_float(pDict.get("maintenance_charges")),

            plot_area=to_float(pDict.get("plot_area"), None),
            builtup_area=to_float(pDict.get("builtup_area"), None),
            facing_direction=pDict.get("facing_direction"),
            garden_area=to_float(pDict.get("garden_area"), None),

            plot_length=to_float(pDict.get("plot_length"), None),
            plot_width=to_float(pDict.get("plot_width"), None),
            water_availability=pDict.get("water_availability"),
            soil_type=pDict.get("soil_type"),

            commercial_type=pDict.get("commercial_type"),
            floor_height=to_float(pDict.get("floor_height"), None),
            loading_capacity=to_float(pDict.get("loading_capacity"), None),
            parking_capacity=to_int(pDict.get("parking_capacity"), None),

            office_type=pDict.get("office_type"),
            furnishing_type=pDict.get("furnishing_type"),
            conference_rooms=to_int(pDict.get("conference_rooms"), None),
            reception_area=pDict.get("reception_area"),

            units_in_complex=to_int(pDict.get("units_in_complex"), None),
            corner_unit=pDict.get("corner_unit"),
            end_unit=pDict.get("end_unit"),
            hoa_fee=to_float(pDict.get("hoa_fee"), None),

            created_by=1,
            updated_by=1
        )
        obj.save()

        # Save Property Type
        if pDict.get("name"):
            own = PropertyType(
                name=pDict.get("name"),
                created_by=1,
                updated_by=1
            )
            own.save()
            obj.property_type = own
            obj.save()

        # Save Images
        if "photo" in files:
            for photo in files.getlist("photo"):
                pho = PropertyImage(
                    property=obj,
                    image=photo,
                    created_by=1,
                    updated_by=1
                )
                pho.save()

        result = True
        message = "Property saved successfully"

    except Exception as e:
        logger.error(f"Error saving property: {str(e)}", exc_info=True)
        message = f"Error saving property: {str(e)}"

    return result, message


@app_logger.functionlogs(log=log_name)
def ajax_operty_save(request):
    result = False
    message = "Failed to save property"
    

    try:
        pDict = request.POST
        files = request.FILES
        
        # Save Property
        obj = Property(
            title=pDict.get("title", ""),
            description=pDict.get("description", ""),
            city=pDict.get("city", ""),
            state=pDict.get("state", ""),
            zipcode=pDict.get("zipcode", ""),
            price=float(pDict.get("price", 0)),
            bedrooms=int(pDict.get("bedrooms", 0)),
            sqft=int(pDict.get("sqft", 0)),
            garage=int(pDict.get("garage", 0)),
            address=pDict.get("address", ""),
            floor_number = int(pDict.get('floor_number') or 0),

            total_floors = int(pDict.get('total_floors') or 0),
            building_age = int(pDict.get('building_age') or 0),
            maintenance_charges = float(pDict.get('maintenance_charges') or 0) ,
            
            plot_area = float(pDict.get('plot_area', 0)) or None,
            builtup_area = float(pDict.get('builtup_area', 0)) or None,
            facing_direction = pDict.get('facing_direction'),
            garden_area = float(pDict.get('garden_area', 0)) or None,

            plot_length = float(pDict.get('plot_length', 0)) or None,
            plot_width = float(pDict.get('plot_width', 0)) or None,
            water_availability = pDict.get('water_availability'),
            soil_type = pDict.get('soil_type'),

            commercial_type = pDict.get('commercial_type'),
            floor_height = float(pDict.get('floor_height', 0)) or None,
            loading_capacity = float(pDict.get('loading_capacity', 0)) or None,
            parking_capacity = int(pDict.get('parking_capacity', 0)) or None,

            office_type = pDict.get('office_type'),
            furnishing_type = pDict.get('furnishing_type'),
            conference_rooms = int(pDict.get('conference_rooms', 0)) or None,
            reception_area = pDict.get('reception_area'),

            units_in_complex = int(pDict.get('units_in_complex', 0)) or None,
            corner_unit = pDict.get('corner_unit'),
            end_unit = pDict.get('end_unit'),
            hoa_fee = float(pDict.get('hoa_fee', 0)) or None,
        
            created_by=1,
            updated_by=1
        )
        obj.save()

        # Save Property Type
        if pDict.get("name"):
            own = PropertyType(
                name=pDict.get("name"),
                created_by=1,
                updated_by=1
            )
            own.save()
            obj.property_type = own
            obj.save()

        # Save Images
        if 'photo' in files:
            for photo in files.getlist('photo'):
                pho = PropertyImage(
                    property=obj,
                    image=photo,
                    created_by=1,
                    updated_by=1
                )
                pho.save()

        result = True
        message = "Property saved successfully"

    except Exception as e:
        logger.error(f"Error saving property: {str(e)}", exc_info=True)
        message = f"Error saving property: {str(e)}"

    return result, message



@app_logger.functionlogs(log=log_name)
def ajax_maintenance_save(request):
    result = False
    message = "Failed to save maintenance"
    
    try:
        pDict = request.POST
        files = request.FILES
        logger.info("Processing maintenance save")
        
        # Create Property first
        maintenance_obj = MaintenanceRequest(
            description=request.POST.get("description", ""),
            urgency=request.POST.get("urgency", ""),
            preferred_date=request.POST.get("preferred_date", ""),
            attachment=request.POST.get("attachment", ""),
            status=request.POST.get("status", ""),
        
            created_by=1,
            updated_by=1
        )
        maintenance_obj.save()
        logger.info("Maintenace object created with ID: %s", maintenance_obj.id)
        
        result = True
        message = "maintenance saved successfully"
        
    except Exception as e:
        logger.exception("Error in ajax_property_save")
        message = f"Error saving maintenance: {str(e)}"
    
    return result, message

@app_logger.functionlogs(log=log_name)
def ajax_eniry_save(request):
    result = False
    message = "Failed to save enquiry"
    
    try:
        pDict = request.POST
        files = request.FILES
        logger.info("Processing enquiry save")
        
        # Create Lead first
        lead_obj = Lead(
            name=request.POST.get("name", ""),
            email=request.POST.get("email", ""),
            phone=request.POST.get("phone", ""),
            location=request.POST.get("location", ""),
            message=request.POST.get("message", ""),
            property_type=request.POST.get("property_type", ""),
            created_by=1,
            updated_by=1
        )
        lead_obj.save()
        logger.info("lead object created with ID: %s", lead_obj.id)

        # -------- Send Email to User -----------
        subject = "Thank you for your enquiry!"
        body = f"""
        Hi {lead_obj.name},

        Thank you for contacting us! 
        We have received your enquiry with the following details:

        📍 Location: {lead_obj.location}
        🏠 Property Type: {lead_obj.property_type}
        📞 Phone: {lead_obj.phone}
        💬 Message: {lead_obj.message}

        Our team will get back to you shortly.

        Regards,  
        Your Company Team
        """

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,    # From
            [lead_obj.email],               # To user who submitted enquiry
            fail_silently=False,
        )

        result = True
        message = "Lead saved and confirmation email sent to user"

    except Exception as e:
        logger.exception("Error in ajax_enquiry_save")
        message = f"Error saving lead: {str(e)}"
    
    return result, message

@app_logger.functionlogs(log=log_name)
def ajax_enquiry_save(request):
    result = False
    message = "Failed to save enquiry"
    
    try:
        pDict = request.POST
        files = request.FILES
        logger.info("Processing enquiry save")
        
        # Create Property first
        lead_obj = Lead(
            name=request.POST.get("name", ""),
            email=request.POST.get("email", ""),
            phone=request.POST.get("phone", ""),
            location=request.POST.get("location", ""),
            message=request.POST.get("message", ""),
            property_type=request.POST.get("property_type", ""),
            
        
            created_by=1,
            updated_by=1
        )
        lead_obj.save()
        logger.info("lead object created with ID: %s", lead_obj.id)
        
        result = True
        message = "lead saved successfully"
        
    except Exception as e:
        logger.exception("Error in ajax_property_save")
        message = f"Error saving lead: {str(e)}"
    
    return result, message