from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
# Create your models here.
from multiselectfield import MultiSelectField
from places.fields import PlacesField


class Chef(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chef')
    name = models.CharField(max_length=500, blank=True)
    phone = models.CharField(max_length=500, blank=True)
    chef_street_address = PlacesField(blank=True)
    chef_flat_number = models.CharField(max_length=500, blank=True)
    city = models.CharField(max_length=500, blank=True)
    postcode = models.CharField(max_length=500, blank=True)
    picture = models.ImageField(upload_to='chef_logo/', blank=True)
    stripe_user_id = models.CharField(max_length=255, blank=True)
    stripe_access_token = models.CharField(max_length=255, blank=True)
    authorized_to_work_in_the_UK = models.BooleanField(default=False)
    available = models.BooleanField(default=False)
    level_2_food_hygiene_certificate = models.FileField(upload_to='chef_certificate/', blank=True, null=True)
    disabled_by_admin = models.BooleanField(default=True)
    note = models.TextField(null=True, blank=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=100, choices=(("Male", "Male"), ("Female", "Female"), ("Other", "Other")),
                              blank=True)
    agree_terms_and_condition = models.BooleanField()
    # Added on Demand
    delivery_time = models.CharField(max_length=255, blank=True, choices=(
        ('Pre-order', 'Pre-order'), ('30-60 min', '30-60 min'), ('60-120 min', '60-120 min')), default='Pre-order')
    # -------------
    cuisine = models.CharField(max_length=255, blank=True, choices=(
        ("British", "British"), ("Chinese", "Chinese"), ("Japanese", "Japanese"), ("Indian", "Indian"),
        ("Italian", "Italian"), ("Pakistani", "Pakistani"), ("Middle East", "Middle East"), ("Nepalese", "Nepalese"),
        ("Mexican", "Mexican"), ("Korean", "Korean"), ("African", "African"), ("Mediterranean", "Mediterranean"),
        ("Caribbean", "Caribbean"), ("French", "French"), ("Latin American", "Latin American"), ("Spanish", "Spanish"),
        ("South East Asian", "South East Asian"), ("European", "European")))
    status = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.id:
            chef = Chef.objects.get(id=self.id)
            if chef.disabled_by_admin == False and self.disabled_by_admin == True:
                send_mail('Slobite: Account Alert  ',
                          'Hello chef! Your account has been disabled by our chef operations team. Kindly, get in touch with us to discuss this matter urgently.',
                          'admin@slobite.com',
                          [chef.user.email], fail_silently=False)
            if chef.disabled_by_admin == True and self.disabled_by_admin == False:
                send_mail('Slobite: Account Alert',
                          'Hello chef! Great news. You account is now active. Start sharing your recipies safely with your neighbourhood. For any further assistance, please contact us at chef@slobite.com or by using the chat support on our website.',
                          'admin@slobite.com',
                          [chef.user.email], fail_silently=False)

        super(Chef, self).save()


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    avatar = models.CharField(max_length=500)
    phone = models.CharField(max_length=500)
    customer_street_address = models.CharField(max_length=500)
    customer_flat_number = models.CharField(max_length=500)
    stripe_id = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.user.get_username()

    def first_name(self):
        return self.user.first_name

    def last_name(self):
        return self.user.last_name

    def email(self):
        return self.user.email


class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver')
    name = models.CharField(max_length=500)
    avatar = models.CharField(max_length=500)
    phone = models.CharField(max_length=500)
    location = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.user.get_full_name()


class Meal(models.Model):
    chef = models.ForeignKey(Chef, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    short_description = models.CharField(max_length=500)
    image = models.ImageField(upload_to='meal_images/', blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                help_text='A 20% tax will be automatically added to the price')
    portion_size = models.CharField(max_length=255, help_text="12 pieces or 12 oz. container or others", blank=True)
    food_type = models.CharField(max_length=255, choices=(
        ('Appetizer', 'Appetizer'), ('Main', 'Main'), ('Side', 'Side'), ('Dessert', 'Dessert')), default=0)
    # Added on demand
    spicy = models.CharField(max_length=255, choices=(
        ('Mild', 'Mild'), ('Medium', 'Medium'), ('Hot', 'Hot'), ('Extreme', 'Extreme')), blank=True, null=True)
    diet = models.CharField(max_length=255, choices=(
        ('Vegan', 'Vegan'), ('Vegetarian', 'Vegetarian')), blank=True, null=True)
    # --------------------
    allergen = MultiSelectField(choices=(
        ('Celery', 'Celery'), ('Gluten', 'Gluten'), ('Crustaceans', 'Crustaceans'), ('Eggs', 'Eggs'), ('Fish', 'Fish'),
        ('Lupin', 'Lupin'), ('Milk', 'Milk'), ('Molluscs', 'Molluscs'), ('Mustard', 'Mustard'), ('Peanuts', 'Peanuts'),
        ('Sesame', 'Sesame'), ('Soybeans', 'Soybeans'), ('Sulphur dioxide', 'Sulphur dioxide'),
        ('Sulphites', 'Sulphites'),
        ('Nuts', 'Nuts')), default=0)
    cuisine = models.CharField(max_length=255, choices=(
        ("British", "British"), ("Chinese", "Chinese"), ("Japanese", "Japanese"), ("Indian", "Indian"),
        ("Italian", "Italian"), ("Pakistani", "Pakistani"), ("Middle East", "Middle East"), ("Nepalese", "Nepalese"),
        ("Mexican", "Mexican"), ("Korean", "Korean"), ("African", "African"), ("Mediterranean", "Mediterranean"),
        ("Caribbean", "Caribbean"), ("French", "French"), ("Latin American", "Latin American"), ("Spanish", "Spanish"),
        ("South East Asian", "South East Asian"), ("European", "European")), default=0)
    availability = models.CharField(max_length=200,
                                    choices=(('Available', 'Available'), ('Unavailable', 'Unavailable')))

    def __str__(self):
        return self.name


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    active = models.BooleanField()

    def __str__(self):
        return self.code


class Order(models.Model):
    COOKING = 1
    READY = 2
    ONTHEWAY = 3
    DELIVERED = 4

    STATUS_CHOICES = (
        (COOKING, "Cooking"),
        (READY, "Ready"),
        (ONTHEWAY, "On the way"),
        (DELIVERED, "Delivered"),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    chef = models.ForeignKey(Chef, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, blank=True, null=True, on_delete=models.CASCADE)
    customer_street_address = models.CharField(max_length=500)
    customer_flat_number = models.CharField(max_length=500)
    phone = models.CharField(max_length=500)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    delivery_instructions = models.CharField(max_length=500, null=False, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    picked_at = models.DateTimeField(blank=True, null=True)
    coupon = models.ForeignKey(Coupon, related_name='order_coupon', to_field='code', blank=True, null=True,
                               on_delete=models.SET_NULL)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pre_order = models.DateTimeField(null=True, blank=True)
    payment_id = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return str(self.id)


class OrderDetails(models.Model):
    order = models.ForeignKey(Order, related_name='order_details', on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=True, null=True)
    delivery_instructions = models.CharField(max_length=500, null=False, blank=True)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class Review(models.Model):
    order = models.ForeignKey(Order, related_name='review_order', on_delete=models.CASCADE)
    chef = models.ForeignKey(Chef, related_name='review_chef', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, related_name='review_customer', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=((1, 1), (2, 2), (3, 3), (4, 4), (5, 5)))
    review_text = models.TextField()
    reply = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
