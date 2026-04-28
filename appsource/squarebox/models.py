from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from config import app_gv as gv
from django.utils import timezone
from django.utils.timezone import now
from django.core.mail import send_mail, EmailMessage


class PropertyType(models.Model):
    name = models.CharField(max_length=100,choices=gv.PROPERTY_TYPE_CHOICES , help_text="Select the type of property, e.g., House, Villa, Plot/Land, Apartment")
    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)


    class Meta:
        db_table = 'property_type'

    def __str__(self):
        return self.name
    
class Property(models.Model):
    """
    Main model for real estate listings.
    """
    # Add this field at the top with your other CharFields
    LISTING_TYPE_CHOICES = [
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
    ]
    
    listing_type = models.CharField(
        max_length=10, 
        choices=LISTING_TYPE_CHOICES, 
        default='sale',
        verbose_name='Listing Type'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='properties',
        db_index=True  # Add index for faster queries
    )

    title = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    price = models.IntegerField()
    bedrooms = models.IntegerField(blank=True, null=True)
    bathrooms = models.IntegerField(blank=True, null=True)
    sqft = models.IntegerField(blank=True, null=True)
    garage = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True,blank=True, null=True)
    list_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    is_hot_selling = models.BooleanField(default=False,blank=True, null=True)
    main_image = models.ImageField(upload_to='ddata/properties/%Y/%m/%d/',blank=True, null=True)
    property_type = models.ForeignKey(PropertyType, on_delete=models.SET_NULL, null=True, blank=True)

    # Apartment specific fields
    floor_number = models.PositiveIntegerField(null=True, blank=True)
    total_floors = models.PositiveIntegerField(null=True, blank=True)
    building_age = models.PositiveIntegerField(null=True, blank=True)
    maintenance_charges = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Villa specific fields
    plot_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    builtup_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    facing_direction = models.CharField(max_length=20, null=True, blank=True)
    garden_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Land specific fields
    plot_length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    plot_width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    water_availability = models.CharField(max_length=20, null=True, blank=True)
    soil_type = models.CharField(max_length=20, null=True, blank=True)
    
    # Commercial specific fields
    commercial_type = models.CharField(max_length=20, null=True, blank=True)
    floor_height = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    loading_capacity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    parking_capacity = models.PositiveIntegerField(null=True, blank=True)
    
    # Office specific fields
    office_type = models.CharField(max_length=20, null=True, blank=True)
    furnishing_type = models.CharField(max_length=20, null=True, blank=True)
    conference_rooms = models.PositiveIntegerField(null=True, blank=True)
    reception_area = models.CharField(max_length=3, choices=(('yes', 'Yes'), ('no', 'No')), null=True, blank=True)
    
    # Townhouse specific fields
    units_in_complex = models.PositiveIntegerField(null=True, blank=True)
    corner_unit = models.CharField(max_length=3, choices=(('yes', 'Yes'), ('no', 'No')), null=True, blank=True)
    end_unit = models.CharField(max_length=3, choices=(('yes', 'Yes'), ('no', 'No')), null=True, blank=True)
    hoa_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_by = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    updated_by = models.CharField(max_length=150, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'property'
        indexes = [
            models.Index(fields=['user', 'datamode']),
            models.Index(fields=['created_by', 'datamode']),
            models.Index(fields=['-updated_on']),
        ]

    def __str__(self):
        return self.title



    

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='ddata/property_images/%Y/%m/%d/')
    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'property_image'

    def __str__(self):
        return f"Image for {self.property.title}"

class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    # user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='maintenance_requests')
    # property = models.ForeignKey('Property', on_delete=models.CASCADE, related_name='maintenance_requests')
    description = models.TextField(help_text="Describe the maintenance issue")
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='medium')
    preferred_date = models.DateField(blank=True, null=True, help_text="Preferred maintenance date")
    attachment = models.FileField(upload_to='maintenance_attachments/', blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    # assigned_to = models.ForeignKey('Agent', on_delete=models.SET_NULL, blank=True, null=True, related_name='assigned_requests')

    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)
    
    class Meta:
        db_table = 'maintenance_request'

    def __str__(self):
        return f"Maintenance Request #{self.id} for {self.property.title} by {self.user.username}"


class Agent(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    bio = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='ddata/agents/', blank=True, null=True)

    class Meta:
        db_table = 'agent'

    def __str__(self):
        return self.name


class Lead(models.Model):

    property = models.ForeignKey(
        Property, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='leads'
    )
    
    # property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='leads')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField(blank=True)
    property_type = models.CharField(max_length=100,blank=True,null=True)
    date_submitted = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=100)
    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'lead'

    def __str__(self):
        return f"{self.name} ({self.property.title})"
    

