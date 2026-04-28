
from django.urls import path
from mck_website import views

app_name = "mck_website"

urlpatterns = [

    # path(".well-known/pki-validation/0021C33903EBC802E268A3D626130F22.txt", views.pki_validation_view, name="pki_validation"),
    path('', views.HomePage.as_view(), name='home_page'),
    path('about/', views.AboutPage.as_view(), name='about_page'),
    path('property-legal-sevices/', views.PropertyLegalServicesPage.as_view(), name='property_legal_services_page'),
    path('our-services/', views.OurServicesPage.as_view(), name='our_services_page'),
    path('privacy-policy/', views.PrivacyPolicyPage.as_view(), name='privacy_policy_page'),
    path('terms/', views.TermsPage.as_view(), name='terms_page'),
    path('solar/',views.SolarPage.as_view(), name='solar_page'),
    path('fencing/',views.FencingPage.as_view(), name='fencing_page'),
    path('land-levelling/',views.LandLevellingPage.as_view(), name='land_levelling_page'),
    path("properties/", views.PropertyPage.as_view(), name="mck_property_page"),
    path('property-details/<int:pk>/', views.PropertyDetailPage.as_view(), name='property_detail'),
    path(
        "property_create/",
        views.PropertyCreatePage.as_view(),
        name="mck_property_create_page",
    ),
    path(
        "maintenances/",
        views.MaintenancesCreatePage.as_view(),
        name="property_maintenance_page",
    ),
    path(
        "enquiry/",
        views.EnquiryCreatePage.as_view(),
        name="property_enquiry_page",
    ),
    path('ajax/property/save/', views.PropertySaveView.as_view(),name='mck_ajax_property_save'),
    path('ajax/maintenances/save/', views.MaintenanceSaveView.as_view(),name='mck_ajax_maintenance_save'),
    path('ajax/lead/save/', views.EnquirySaveView.as_view(),name='mck_ajax_enquiry_save'),


    path('dashboard/',  views.UserDashboardPage.as_view(), name='dashboard'),
    path('dashboard/property/delete/<int:pk>/',  views.UserPropertyDeleteView.as_view(), name='delete_property'),
    path('dashboard/property/edit/<int:pk>/',  views.UserPropertyEditPage.as_view(), name='edit_property'),
    path('dashboard/property/edit/<int:pk>/', views.UserPropertyEditPage.as_view(), name='edit_property'),
    path('dashboard/property/update/<int:pk>/', views.UserPropertyUpdateView.as_view(), name='update_property'),
    path('dashboard/property/image/delete/<int:pk>/', views.UserPropertyImageDeleteView.as_view(), name='delete_property_image'),
    # In urls.py
path('debug-properties/', views.DebugPropertiesView.as_view(), name='debug_properties'),
]