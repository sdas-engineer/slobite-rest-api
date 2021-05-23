from django.contrib import admin

# Register your models here.
from urbanshef.models import Chef, Customer, Driver, Meal, Order, OrderDetails, Review, Coupon

admin.site.register(Chef)
admin.site.register(Customer)
admin.site.register(Driver)
admin.site.register(Meal)


class OrderModel(admin.ModelAdmin):
    class Meta:
        model = Order

    list_display = ['__str__']
    list_filter = ['created_at']


admin.site.register(Order, OrderModel)
admin.site.register(OrderDetails)
admin.site.register(Review)
admin.site.register(Coupon)
