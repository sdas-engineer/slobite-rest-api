from django.contrib import admin

# Register your models here.
from urbanshef.models import Chef, Customer, Driver, Meal, Order, OrderDetails, Review, Coupon


class ChefModel(admin.ModelAdmin):
    class Meta:
        model = Chef

    list_display = ['__str__', 'phone', 'available', 'disabled_by_admin', 'gender', 'cuisine']
    list_filter = ['available', 'disabled_by_admin', 'gender', 'cuisine']
    list_display_links = ['__str__']
    search_fields = ['phone', 'name']
    list_per_page = 25


admin.site.register(Chef, ChefModel)


class CustomerModel(admin.ModelAdmin):
    class Meta:
        model = Customer

    list_display = ['__str__', 'first_name', 'last_name','email', 'phone']
    list_display_links = ['__str__']
    search_fields = ['phone', 'name']
    list_per_page = 25


admin.site.register(Customer, CustomerModel)


class DriverModel(admin.ModelAdmin):
    class Meta:
        model = Driver

    list_display = ['__str__', 'phone']
    list_display_links = ['__str__']
    search_fields = ['phone', 'name']
    list_per_page = 25


admin.site.register(Driver, DriverModel)


class MealModel(admin.ModelAdmin):
    class Meta:
        model = Meal

    list_display = ['__str__', 'chef', 'price', 'food_type', 'allergen', 'cuisine', 'availability']
    list_display_links = ['__str__']
    search_fields = ['name', 'food_type', 'allergen', 'cuisine']
    list_filter = ['availability', 'food_type', 'allergen', 'cuisine', ]
    list_per_page = 25


admin.site.register(Meal, MealModel)


class OrderModel(admin.ModelAdmin):
    class Meta:
        model = Order

    list_display = ['__str__', 'chef', 'customer', 'total', 'status']
    list_filter = ['created_at', 'status']
    list_display_links = ['__str__']
    list_per_page = 25


admin.site.register(Order, OrderModel)


class OrderDetailsModel(admin.ModelAdmin):
    class Meta:
        model = OrderDetails

    list_display = ['__str__', 'meal', 'quantity', 'delivery_charge', 'sub_total']
    list_per_page = 25


admin.site.register(OrderDetails, OrderDetailsModel)


class ReviewModel(admin.ModelAdmin):
    class Meta:
        model = Review

    list_display = ['__str__', 'chef', 'customer', 'rating']
    list_filter = ['rating']
    list_per_page = 25
    search_fields = ['chef', 'customer']


admin.site.register(Review, ReviewModel)


class CouponModel(admin.ModelAdmin):
    class Meta:
        model = Coupon

    list_display = ['__str__', 'valid_from', 'valid_to', 'active']
    list_filter = ['valid_from', 'valid_to', 'active']
    list_per_page = 25
    search_fields = ['code']


admin.site.register(Coupon, CouponModel)
