from django.contrib import admin

# Register your models here.
from urbanshef.models import Chef, Customer, Driver, Meal, Order, OrderDetails, Review

admin.site.register(Chef)
admin.site.register(Customer)
admin.site.register(Driver)
admin.site.register(Meal)
admin.site.register(Order)
admin.site.register(OrderDetails)
admin.site.register(Review)
