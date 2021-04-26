from django.utils.encoding import smart_text
from places.fields import PlacesField
from rest_framework import serializers

from urbanshef.models import Chef, \
    Meal, \
    Customer, \
    Driver, \
    Order, \
    OrderDetails, Review


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
                  "level_2_food_hygiene_certificate", "disabled_by_admin", "note", "bio", "date_of_birth", "gender")


class MealSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, meal):
        request = self.context.get('request')
        image_url = meal.image.url
        return request.build_absolute_uri(image_url)

    class Meta:
        model = Meal
        fields = ("id", "name", "short_description", "image", "price", 'availability')


# ORDER SERIALIZER
class OrderCustomerSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="user.get_full_name")

    class Meta:
        model = Customer
        fields = ("id", "name", "avatar", "phone", "customer_street_address", "customer_flat_number")


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
    customer = OrderCustomerSerializer()
    chef = OrderChefSerializer()
    order_details = OrderDetailsSerializer(many=True)
    status = serializers.ReadOnlyField(source="get_status_display")

    class Meta:
        model = Order
        fields = ("id", "customer", "chef", "order_details", "total", "status", "customer_street_address",
                  "customer_flat_number", "phone", "delivery_instructions")


class OrderCreateSerializer(serializers.ModelSerializer):
    access_token = serializers.CharField(max_length=200, allow_blank=False, allow_null=False)
    chef_id = serializers.IntegerField()
    order_details = serializers.CharField()
    stripe_token=serializers.CharField()

    class Meta:
        model = Order
        fields = (
            'access_token', 'chef_id','stripe_token','delivery_charge', "customer_street_address", "customer_flat_number", "phone",
            'order_details')


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
