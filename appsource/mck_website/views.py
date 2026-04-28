"""
Views - VLR Website App
"""

from django.http import HttpResponse
import os
from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404
from config import app_logger
from config import app_seo as seo
from squarebox.models import *
from mck_website.api import *
from mck_website.models import *
from django.urls import reverse 
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from mck_auth import build_table as bt
from mck_auth import role_validations as rv
from squarebox import api
from squarebox import forms
from squarebox import models
from django.core.paginator import Paginator
from django.db.models import Q

LOG_NAME = "app"
logger = app_logger.createLogger(LOG_NAME)


def pki_validation_view(request):
    file_path = os.path.join(settings.BASE_DIR, "mck_website", "templates", "verify.txt")
    try:
        with open(file_path, "r") as file:
            content = file.read()
        return HttpResponse(content, content_type="text/plain")
    except FileNotFoundError:
        return HttpResponse("File not found", status=404)



class HomePage(TemplateView):
    """
    Home Page
    """
    template_name = "home.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("home_page")

        context["property"] = Property.objects.exclude(datamode='D').order_by('-updated_on')
        context["property_type"] = PropertyType.objects.exclude(datamode='D').order_by('-updated_on')
        context["property_image"] = PropertyImage.objects.exclude(datamode='D').order_by('-updated_on')
        context["lead"] = Lead.objects.exclude(datamode='D').order_by('-updated_on')
        context["cities"] = Property.objects.exclude(datamode='D') \
                                            .values_list('city', flat=True) \
                                            .distinct() \
                                            .order_by('city')
        context["property"] = (
            Property.objects.exclude(datamode='D')
            .prefetch_related(
                Prefetch('images', queryset=PropertyImage.objects.exclude(datamode='D'))
            )
            .order_by('-updated_on')
)

        logger.info(request.GET)
        return render(request, self.template_name, context)


class PropertyPage(TemplateView):
    template_name = "property_page.html"

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all properties excluding deleted ones
        qs = Property.objects.exclude(datamode='D')
        
        # Apply filters
        city = request.GET.get('city')
        listing_type = request.GET.get("listing_type")
        property_type = request.GET.get('property_type')
        budget = request.GET.get('budget')
        sort = request.GET.get('sort', 'newest')

        if city:
            qs = qs.filter(city__icontains=city)

        if property_type:
            qs = qs.filter(property_type__name__iexact=property_type)

        if listing_type:
            qs = qs.filter(listing_type__iexact=listing_type)

        if budget:
            if budget == "Below 100k":
                qs = qs.filter(price__lt=100000)
            elif budget == "100k - 300k":
                qs = qs.filter(price__range=(100000, 300000))
            elif budget == "Above 300k":
                qs = qs.filter(price__gt=300000)

        # Apply sorting
        if sort == 'price_low':
            qs = qs.order_by('price')
        elif sort == 'price_high':
            qs = qs.order_by('-price')
        else:  # newest
            qs = qs.order_by('-updated_on')

       

        # Pagination
        paginator = Paginator(qs, 9)  # Show 9 properties per page
        page_number = request.GET.get('page')
        properties = paginator.get_page(page_number)
        
        # Prefetch related images
        properties.object_list = properties.object_list.prefetch_related(
            Prefetch(
                'images',  
                queryset=PropertyImage.objects.exclude(datamode='D').order_by('-updated_on'),
                to_attr='property_images_list'  
            )
        )

        context["properties"] = properties
        context["property_types"] = PropertyType.objects.exclude(datamode='D').order_by('-updated_on')
        context["cities"] = (
            Property.objects.exclude(datamode='D')
            .values_list('city', flat=True)
            .distinct()
            .order_by('city')
        )

        return render(request, self.template_name, context)


class PropertyDetailPage(TemplateView):
    template_name = "resources.html"

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        property_id = kwargs.get('pk')  # from URL
        property_obj = get_object_or_404(
            Property.objects.prefetch_related(
                Prefetch(
                    'images',
                    queryset=PropertyImage.objects.exclude(datamode='D').order_by('-updated_on')
                )
            ),
            pk=property_id
        )

        context["property"] = property_obj
        return render(request, self.template_name, context)

class PropertyCreatePage(TemplateView):
    template_name = "pages/property_create.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_kwargs"] = seo.get_page_tags("property_create")
        property = Property.objects.exclude(datamode='D').order_by('-updated_on')
        context["property"] = property
        logger.info(request.GET)
        return render(request, self.template_name, context)
    
    
class MaintenancesCreatePage(TemplateView):
    template_name = "pages/faq.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_kwargs"] = seo.get_page_tags("maintenance")
        maintenance = MaintenanceRequest.objects.exclude(datamode='D').order_by('-updated_on')
        context["maintenance"] = maintenance
        logger.info(request.GET)
        return render(request, self.template_name, context)
    

class PropertySaveView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            logger.info("Received property save request")
            logger.info("POST data: %s", request.POST)
            logger.info("FILES data: %s", request.FILES)
            
            result, message = api.ajax_property_save(request)
            if result:
                logger.info("Property saved successfully")
                return JsonResponse({"status": "success", "message": message})
            else:
                logger.error("Failed to save property: %s", message)
                return JsonResponse({"status": "fail", "message": message}, status=400)
                
        except Exception as e:
            logger.exception("Unexpected error in PropertySaveView")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
        

class MaintenanceSaveView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            logger.info("Received Maintenance save request")
            logger.info("POST data: %s", request.POST)
            logger.info("FILES data: %s", request.FILES)
            
            result, message = api.ajax_maintenance_save(request)
            if result:
                logger.info("maintenance saved successfully")
                return JsonResponse({"status": "success", "message": message})
            else:
                logger.error("Failed to save maintenance: %s", message)
                return JsonResponse({"status": "fail", "message": message}, status=400)
                
        except Exception as e:
            logger.exception("Unexpected error in maintenanceSaveView")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
        
        
class EnquiryCreatePage(TemplateView):
    template_name = "includes/enquiry.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_kwargs"] = seo.get_page_tags("lead")
        lead = Lead.objects.exclude(datamode='D').order_by('-updated_on')
        context["lead"] = lead
        property_type = request.GET.get('property_type', '')
        context["selected_property_type"] = property_type  
        logger.info(request.GET)
        return render(request, self.template_name, context)

class EnquirySaveView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            logger.info("Received lead save request")
            logger.info("POST data: %s", request.POST)
            logger.info("FILES data: %s", request.FILES)
            
            result, message = api.ajax_enquiry_save(request)
            if result:
                logger.info("lead saved successfully")
                return JsonResponse({"status": "success", "message": message})
            else:
                logger.error("Failed to save lead: %s", message)
                return JsonResponse({"status": "fail", "message": message}, status=400)
                
        except Exception as e:
            logger.exception("Unexpected error in leadSaveView")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

class AboutPage(TemplateView):
    """
    About Page
    """
    template_name = "about.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("about_page")
        logger.info(request.GET)
        return render(request, self.template_name, context)
    
class OurServicesPage(TemplateView):
    """
    ourservices Page
    """
    template_name = "our_services.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("about_page")
        logger.info(request.GET)
        return render(request, self.template_name, context)
    

class PrivacyPolicyPage(TemplateView):
    """
    ourservices Page
    """
    template_name = "privacy_policy.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("privacy_policy_page")
        logger.info(request.GET)
        return render(request, self.template_name, context)

class TermsPage(TemplateView):
    """
    terms Page
    """
    template_name = "terms.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("terms_page")
        logger.info(request.GET)
        return render(request, self.template_name, context)
    
class PropertyLegalServicesPage(TemplateView):
    """
    terms Page
    """
    template_name = "property_legal_services.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("property_legal_services_page")
        logger.info(request.GET)
        return render(request, self.template_name, context)

class SolarPage(TemplateView):
    template_name = "solar.html"
    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("solar")
        logger.info(request.GET)
        return render(request, self.template_name, context)


class FencingPage(TemplateView):
    template_name = "fencing.html"
    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("fencing")
        logger.info(request.GET)
        return render(request, self.template_name, context)
    
class LandLevellingPage(TemplateView):
    template_name = "pages/land_leveling.html"
    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("land_levelling")
        logger.info(request.GET)
        return render(request, self.template_name, context)


# Add these views to your existing mck_website/views.py
# In mck_website/views.py, update your UserDashboardPage:
# In mck_website/views.py - Fix the UserDashboardPage
# mck_website/views.py - Complete updated UserDashboardPage

# mck_website/views.py
# mck_website/views.py - Updated UserDashboardPage without the property filter
# =====================================================================
# FIXED views.py - Dashboard / Delete / Edit
# =====================================================================
# Required imports (add to your existing imports if missing):
# =====================================================================
# DASHBOARD VIEW (debug-rich version) — replace your UserDashboardPage
# Renamed context key to `my_properties` so nothing else can shadow it.
# Logs the SQL + counts so you can see exactly what's happening.
# =====================================================================
import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
# from squarebox.models import Property, PropertyType, PropertyImage, Lead, MaintenanceRequest

logger = logging.getLogger(__name__)


class UserDashboardPage(LoginRequiredMixin, TemplateView):
    template_name = "user/dashboards.html"
    login_url = '/auth/website/login/'
    raise_exception = False  # redirects unauthenticated users instead of 403

    def get(self, request, *args, **kwargs):
        context = {}
        try:
            context = super().get_context_data(**kwargs)
        except Exception:
            context = {}

        try:
            context['page_kwargs'] = seo.get_page_tags("dashboard")
        except Exception:
            context['page_kwargs'] = {}

        user = request.user

        # ---- Build queryset (broad: 3 ownership patterns) ----
        qs = Property.objects.filter(
            Q(user=user) |
            Q(created_by=str(user.id)) |
            Q(created_by=user.username)
        ).exclude(datamode='D').select_related('property_type').prefetch_related(
            Prefetch('images', queryset=PropertyImage.objects.filter(datamode='A'))
        ).order_by('-updated_on').distinct()

        # ---- DEBUG: print to console / logs ----
        print('=' * 70)
        print(f'[DASHBOARD DEBUG] user.id={user.id}  username={user.username}  email={user.email}')
        print(f'[DASHBOARD DEBUG] properties count = {qs.count()}')
        print(f'[DASHBOARD DEBUG] SQL = {qs.query}')
        print(f'[DASHBOARD DEBUG] First 3 = {list(qs.values("id", "title", "created_by", "user_id", "datamode")[:3])}')
        print('=' * 70)
        logger.warning(f'[DASHBOARD] user={user.username} property_count={qs.count()}')

        # ---- Paginate ----
        paginator = Paginator(qs, 10)
        page_number = request.GET.get('page', 1)
        properties_page = paginator.get_page(page_number)

        # ---- Stats ----
        total_properties = qs.count()
        published_properties = qs.filter(is_published=True).count()

        # ---- Enquiries ----
        try:
            user_enquiries = Lead.objects.filter(
                Q(email=user.email) | Q(property__in=qs)
            ).exclude(datamode='D').order_by('-created_on').distinct()[:20]
            total_enquiries = user_enquiries.count() if hasattr(user_enquiries, 'count') else len(list(user_enquiries))
        except Exception as e:
            logger.exception('Lead query failed')
            user_enquiries = []
            total_enquiries = 0

        # ---- Maintenance ----
        try:
            user_maintenance = MaintenanceRequest.objects.filter(
                Q(created_by=str(user.id)) | Q(created_by=user.username)
            ).exclude(datamode='D').order_by('-created_on')
            total_maintenance = user_maintenance.count()
        except Exception:
            user_maintenance = []
            total_maintenance = 0

        # ---- Context ----
        # Use a UNIQUE key (`my_properties`) to avoid being shadowed by
        # anything in base.html / context_processors / middleware.
        context.update({
            'user': user,
            'my_properties': properties_page,
            'my_properties_list': list(properties_page),  # plain list backup
            'total_properties': total_properties,
            'published_properties': published_properties,
            'draft_properties': total_properties - published_properties,
            'user_enquiries': user_enquiries,
            'total_enquiries': total_enquiries,
            'user_maintenance': user_maintenance,
            'total_maintenance': total_maintenance,
            'is_paginated': properties_page.has_other_pages(),
            'page_obj': properties_page,
            # Debug values surfaced in template:
            'debug_count': total_properties,
            'debug_user_id': user.id,
            'debug_username': user.username,
            'debug_first_titles': list(qs.values_list('title', flat=True)[:5]),
        })

        return render(request, self.template_name, context)


# =====================================================================
# FIXED views.py - Dashboard / Delete / Edit
# =====================================================================
# Required imports (add to your existing imports if missing):
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
# from squarebox.models import Property, PropertyType, PropertyImage, Lead, MaintenanceRequest
# (use your real import path)

# =====================================================================
# DELETE PROPERTY  (FIXED: previous filter compared CharField to User)
# =====================================================================
class UserPropertyDeleteView(TemplateView):
    """Soft-delete a user's property."""

    @app_logger.functionlogs(log=LOG_NAME)
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"status": "error", "message": "You need to login first"},
                status=401
            )

        property_id = kwargs.get('pk')
        user = request.user

        try:
            # CORRECT: match user via FK OR via stringified id OR username
            property_obj = Property.objects.filter(pk=property_id).filter(
                Q(user=user) |
                Q(created_by=str(user.id)) |
                Q(created_by=user.username)
            ).first()

            if not property_obj:
                return JsonResponse(
                    {"status": "error", "message": "Property not found or access denied"},
                    status=404
                )

            property_obj.datamode = 'D'
            property_obj.updated_by = str(user.id)
            property_obj.save()

            logger.info(f"Property {property_id} deleted by user {user.email}")
            return JsonResponse(
                {"status": "success", "message": "Property deleted successfully"}
            )
        except Exception as e:
            logger.exception("Error deleting property")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


# =====================================================================
# EDIT PROPERTY  (FIXED: same filter bug)
# =====================================================================
class UserPropertyEditPage(TemplateView):
    """Edit a user's property."""
    template_name = "user/edit.html"

    def _get_user_property(self, property_id, user):
        """Return the property if owned by user, else None."""
        return Property.objects.filter(pk=property_id).filter(
            Q(user=user) |
            Q(created_by=str(user.id)) |
            Q(created_by=user.username)
        ).first()

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('mck_auth:website_signin')

        context = super().get_context_data(**kwargs)
        property_id = kwargs.get('pk')
        property_obj = self._get_user_property(property_id, request.user)

        if not property_obj:
            return redirect('mck_website:dashboard')

        context['property'] = property_obj
        context['property_types'] = PropertyType.objects.exclude(datamode='D')
        context['property_images'] = PropertyImage.objects.filter(
            property=property_obj
        ).exclude(datamode='D')

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "Unauthorized"}, status=401)

        property_id = kwargs.get('pk')
        property_obj = self._get_user_property(property_id, request.user)

        if not property_obj:
            return JsonResponse(
                {"status": "error", "message": "Property not found or access denied"},
                status=404
            )

        try:
            result, message = api.ajax_property_update(request, property_id)
            if result:
                return JsonResponse({"status": "success", "message": message})
            return JsonResponse({"status": "fail", "message": message}, status=400)
        except Exception as e:
            logger.exception("Error updating property")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

class UserPropertyUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            property_obj = get_object_or_404(Property, id=pk, user=request.user)
            
            # Update basic fields
            property_obj.title = request.POST.get('title')
            property_obj.description = request.POST.get('description')
            property_obj.price = request.POST.get('price')
            property_obj.city = request.POST.get('city')
            property_obj.address = request.POST.get('address')
            property_obj.state = request.POST.get('state')
            property_obj.zipcode = request.POST.get('zipcode')
            property_obj.listing_type = request.POST.get('listing_type')
            property_obj.bedrooms = request.POST.get('bedrooms') or None
            property_obj.bathrooms = request.POST.get('bathrooms') or None
            property_obj.sqft = request.POST.get('sqft') or None
            property_obj.garage = request.POST.get('garage') or 0
            
            # Handle is_published (convert string to boolean)
            is_published_str = request.POST.get('is_published')
            property_obj.is_published = is_published_str == 'true'
            
            # Update property type
            property_type_id = request.POST.get('property_type')
            if property_type_id:
                property_obj.property_type_id = property_type_id
            
            property_obj.updated_by = str(request.user.id)
            property_obj.save()
            
            # Handle new images
            new_images = request.FILES.getlist('new_images')
            for image in new_images:
                PropertyImage.objects.create(
                    property=property_obj,
                    image=image,
                    created_by=str(request.user.id),
                    updated_by=str(request.user.id)
                )
            
            return JsonResponse({"status": "success", "message": "Property updated successfully"})
            
        except Property.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Property not found"}, status=404)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


class UserPropertyImageDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            image = get_object_or_404(PropertyImage, id=pk, property__user=request.user)
            image.delete()  # Or soft delete: image.datamode = 'D'; image.save()
            return JsonResponse({"status": "success", "message": "Image deleted successfully"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
# Add this to views.py temporarily for debugging
class DebugPropertiesView(TemplateView):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Not authenticated"}, status=401)
        
        user = request.user
        properties_by_id = Property.objects.filter(created_by=str(user.id)).exclude(datamode='D').values('id', 'title', 'created_by')
        properties_by_username = Property.objects.filter(created_by=user.username).exclude(datamode='D').values('id', 'title', 'created_by')
        properties_by_user_field = Property.objects.filter(user=user).exclude(datamode='D').values('id', 'title', 'user')
        
        return JsonResponse({
            "user_id": user.id,
            "user_username": user.username,
            "user_email": user.email,
            "properties_by_id": list(properties_by_id),
            "properties_by_username": list(properties_by_username),
            "properties_by_user_field": list(properties_by_user_field),
            "all_properties": list(Property.objects.exclude(datamode='D').values('id', 'title', 'created_by', 'user'))
        })
