from rest_framework import serializers

from urbanshef.models import Chef, \
    Meal, \
    Customer, \
    Driver, \
    Order, \
    OrderDetails, Review, Coupon


class PlacesSerializer(serializers.Serializer):
    place = serializers.CharField(max_length=255)
    latitude = serializers.CharField(max_length=200)
    longitude = serializers.CharField(max_length=200)

    class Meta:
        fields = ['place', 'latitude', 'longitude']


class ChefSerializer(serializers.ModelSerializer):
    chef_street_address = PlacesSerializer(many=False)

    def get_picture(self, chef):
        request = self.context.get('request')
        picture_url = chef.picture.url
        return request.build_absolute_uri(picture_url)

    class Meta:
        model = Chef
        fields = ("id", "name", "phone", "chef_street_address", "chef_flat_number", "city",
                  "postcode", "picture", "stripe_user_id", "stripe_access_token", "available",
                  "level_2_food_hygiene_certificate", "disabled_by_admin", "note", "bio", "date_of_birth", "gender",
                  "delivery_time",
                  "cuisine")


class MealSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, meal):
        request = self.context.get('request')
        image_url = meal.image.url
        return request.build_absolute_uri(image_url)

    class Meta:
        model = Meal
        fields = ("id", "name", "short_description", "image", "price", 'availability', 'spicy', 'diet')


# ORDER SERIALIZER
class OrderCustomerSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="user.get_full_name")

    class Meta:
        model = Customer
        fields = ("id", "name", "avatar", "phone", "customer_street_address")


class OrderDriverSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="user.get_full_name")

    class Meta:
        model = Driver
        fields = ("id", "name", "avatar", "phone", "location")


class OrderChefSerializer(serializers.ModelSerializer):
    chef_street_address = PlacesSerializer(many=False)

    class Meta:
        model = Chef
        fields = ("id", "name", "phone", "chef_street_address", "chef_flat_number", "city", "postcode")


class OrderMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ("id", "name", "price")


class OrderDetailsSerializer(serializers.ModelSerializer):
    meal = OrderMealSerializer()

    class Meta:
        model = OrderDetails
        fields = ("id", "meal", "quantity", "sub_total")


class OrderSerializer(serializers.ModelSerializer):
    customer = OrderCustomerSerializer(many=False)
    chef = OrderChefSerializer()
    order_details = OrderDetailsSerializer(many=True)
    status = serializers.ReadOnlyField(source="get_status_display")

    class Meta:
        model = Order
        fields = ("id", "customer", "chef", "order_details", "total", "status", "customer_street_address",
                  "customer_flat_number", "service_charge", "phone", "delivery_instructions", 'pre_order')


class OrderCreateSerializer(serializers.ModelSerializer):
    access_token = serializers.CharField(max_length=200, required=True)
    chef_id = serializers.IntegerField()
    order_details = serializers.CharField()
    coupon = serializers.CharField(max_length=100, required=False)
    pre_order = serializers.DateTimeField(required=False)

    # def to_internal_value(self, data):
    #     if data.get('pre_order') == '':
    #         data['pre_order'] = None
    #     return super().to_internal_value(data)

    class Meta:
        model = Order
        fields = (
            'access_token', 'chef_id', 'delivery_charge', "service_charge", "customer_street_address",
            "customer_flat_number", "phone", 'order_details', 'delivery_instructions', 'coupon', 'pre_order', 'payment_id')


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ['reply']


class ChefContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chef
        fields = ['phone']


class ChefBioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chef
        fields = ['bio']


class ChefAvgRatingSerializer(serializers.Serializer):
    rating = serializers.DecimalField(max_digits=2, decimal_places=1)
    number_of_reviews = serializers.IntegerField()


class MealAllergensSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal,
        fields = ['allergen']


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'valid_from', 'valid_to', 'discount', 'active']
        read_only_fields = ['id', 'valid_from', 'valid_to', 'discount', 'active']


class PaymentMethodSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=100, required=True, label='Payment method type')
    card_number = serializers.CharField(max_length=30, required=True, label='Card number')
    exp_month = serializers.IntegerField(required=True, label='Expiry month')
    exp_year = serializers.IntegerField(required=True, label='Expiry year')
    cvc = serializers.CharField(max_length=20, required=True)

    class Meta:
        fields = ['type', 'card_number', 'exp_month', 'exp_year', 'cvc']


class PaymentIntentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    currency = serializers.CharField(max_length=100, required=True)
    access_token = serializers.CharField(max_length=200, required=True)

    class Meta:
        fields = ['amount', 'currency', 'access_token']


class PaymentIntentModifySerializer(serializers.Serializer):
    id = serializers.CharField(max_length=200, required=True, label='Payment ID')
    payment_method = serializers.CharField(max_length=200, required=True)

    class Meta:
        fields = ['id', 'payment_method']


class CheckPaymentSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=100, required=True, label='Payment ID')

    class Meta:
        fields = ['id']


class PaymentIntentConfirmSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=100, required=True, label='Payment ID')
    payment_method = serializers.CharField(max_length=100, required=True)

    class Meta:
        fields = ['id', 'payment_method']


class PaymentIntentCancelSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=200, required=True, label='Payment ID')

    class Meta:
        fields = ['id']
