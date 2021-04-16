import json

import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.models import AccessToken
from rest_framework import status, generics
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from twilio.rest import Client


from urbanshef.models import Chef, Meal, Order, OrderDetails, Review
from urbanshef.serializers import ChefSerializer, \
    MealSerializer, \
    OrderSerializer, ReviewSerializer, ChefContactSerializer, ChefBioSerializer, ChefAvgRatingSerializer
from urbanshefapp.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY


##############
# CUSTOMERS
##############


class CustomerGetChefs(generics.ListAPIView):
    serializer_class = ChefSerializer
    permission_classes = []
    authentication_classes = []
    queryset = Chef.objects.filter(disabled_by_admin=False, available=True).order_by("-id")

    def get(self, request, *args, **kwargs):
        c = self.get_queryset()
        if request.GET.get('cuisine'):
            meal = Meal.objects.filter(chef__available=True, chef__disabled_by_admin=False,
                                       cuisine=request.GET.get('cuisine')).values('chef_id').distinct()
            if meal.count() != 0:
                l = []
                for m in meal:
                    l.append(m['chef_id'])
                c = c.filter(id__in=l)
            else:
                c = []
        chefs = self.get_serializer(
            c,
            many=True,
            context={"request": request}
        ).data
        return Response({'chefs': chefs}, status=status.HTTP_200_OK)


class CustomerGetMeals(APIView):
    def get(self, request, chef_id):
        try:
            chef = Chef.objects.get(id=chef_id)
            if chef.available is False:
                return Response({'message': 'Chef is unavailable now'},
                                status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)
            if chef.disabled_by_admin is True:
                return Response({'message': 'Chef is disabled by Urbanshef'}, status=status.HTTP_423_LOCKED)
            meals = MealSerializer(
                Meal.objects.filter(chef_id=chef_id, availability='Available').order_by("-id"),
                many=True,
                context={"request": request}
            ).data
            return Response({"meals": meals}, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'No Chef found'}, status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
def customer_add_order(request):
    """
        params:
            access_token
            chef_id
            customer_street_address
            customer_flat_number
            phone
            order_details (json format), example:
                [{"meal_id": 1, "quantity": 2},{"meal_id": 2, "quantity": 3}]
            delivery_charge
            stripe_token

        return:
            {"status": "success"}
    """

    if request.method == "POST":
        # Get token
        access_token = AccessToken.objects.get(token=request.POST.get("access_token"),
                                               expires__gt=timezone.now())

        # Get profile
        customer = access_token.user.customer

        # Get Stripe token
        stripe_token = request.POST["stripe_token"]

        # Check whether customer has any order that is not delivered
        if Order.objects.filter(customer=customer).exclude(status=Order.DELIVERED):
            return JsonResponse({"status": "failed", "error": "Your last order must be completed."})

        # Check Address
        if not request.POST["customer_street_address"]:
            return JsonResponse({"status": "failed", "error": "Address is required."})

        # Get Order Details
        order_details = json.loads(request.POST["order_details"])

        order_total = 0
        for meal in order_details:
            order_total += Meal.objects.get(id=meal["meal_id"]).price * meal["quantity"]
        order_total_including_charge = order_total + 3 + ((order_total + 3) * 0.2)
        if len(order_details) > 0:

            # Step 1: Create a charge: this will charge customer's card
            charge = stripe.Charge.create(
                amount=int(order_total_including_charge),  # Amount in pence
                currency="gbp",
                source=stripe_token,
                description="Urbanshef Order"
            )

            if charge.status != "failed":
                # Step 2 - Create an Order
                order = Order.objects.create(
                    customer=customer,
                    chef_id=request.POST["chef_id"],
                    total=order_total_including_charge,
                    status=Order.COOKING,
                    customer_street_address=request.POST["customer_street_address"],
                    customer_flat_number=request.POST["customer_flat_number"],
                    # city=request.POST["city"],
                    # postcode=request.POST["postcode"],
                    tax=(order_total + 3) * 0.2,
                    phone=request.POST.get["phone"],
                    delivery_charge=3
                )

                # Step 3 - Create Order details
                for meal in order_details:
                    OrderDetails.objects.create(
                        order=order,
                        meal_id=meal["meal_id"],
                        quantity=meal["quantity"],
                        sub_total=Meal.objects.get(id=meal["meal_id"]).price * meal["quantity"]
                    )
                message_to_broadcast = ("Hello chef! You have a new order. View your Urbanshef dashboard to fulfill the order!")
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                try:
                    client.messages.create(to=order.chef.phone, from_=settings.TWILIO_NUMBER, body=message_to_broadcast)
                except:
                    print('Unable to send message to ' + order.chef.phone)
                send_mail('Urbanshef: New Order Alert',
                          'Hello chef! You have a new order. View your Urbanshef dashboard to fulfill the order!',
                          'no-reply@urbanshef.com',
                          [order.chef.user.email], fail_silently=False)
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({"status": "failed", "error": "Payment failed."})


def customer_get_latest_order(request):
    access_token = AccessToken.objects.get(token=request.GET.get("access_token"),
                                           expires__gt=timezone.now())

    customer = access_token.user.customer
    order = OrderSerializer(Order.objects.filter(customer=customer).last()).data

    return JsonResponse({"order": order})


def customer_driver_location(request):
    access_token = AccessToken.objects.get(token=request.GET.get("access_token"),
                                           expires__gt=timezone.now())

    customer = access_token.user.customer

    # Get driver's location related to this customer's current order.
    current_order = Order.objects.filter(customer=customer, status=Order.DELIVERED).last()
    location = current_order.driver.location

    return JsonResponse({"location": location})


##############
# CHEF
##############

def chef_order_notification(request, last_request_time):
    notification = Order.objects.filter(chef=request.user.chef,
                                        created_at__gt=last_request_time).count()

    return JsonResponse({"notification": notification})


##############
# DRIVERS
##############

def driver_get_ready_orders(request):
    orders = OrderSerializer(
        Order.objects.filter(status=Order.READY, driver=None).order_by("-id"),
        many=True
    ).data

    return JsonResponse({"orders": orders})


@csrf_exempt
# POST
# params: access_token, order_id
def driver_pick_order(request):
    if request.method == "POST":
        # Get token
        access_token = AccessToken.objects.get(token=request.POST.get("access_token"),
                                               expires__gt=timezone.now())

        # Get Driver
        driver = access_token.user.driver

        # Check if driver can only pick up one order at the same time
        if Order.objects.filter(driver=driver).exclude(status=Order.ONTHEWAY):
            return JsonResponse({"status": "failed", "error": "You can only pick one order at the same time."})

        try:
            order = Order.objects.get(
                id=request.POST["order_id"],
                driver=None,
                status=Order.READY
            )
            order.driver = driver
            order.status = Order.ONTHEWAY
            order.picked_at = timezone.now()
            order.save()

            return JsonResponse({"status": "success"})

        except Order.DoesNotExist:
            return JsonResponse({"status": "failed", "error": "This order has been picked up by another rider."})

    return JsonResponse({})


# GET params: access_token
def driver_get_latest_order(request):
    # Get token
    access_token = AccessToken.objects.get(token=request.GET.get("access_token"),
                                           expires__gt=timezone.now())

    driver = access_token.user.driver
    order = OrderSerializer(
        Order.objects.filter(driver=driver).order_by("picked_at").last()
    ).data

    return JsonResponse({"order": order})


# POST params: access_token, order_id
@csrf_exempt
def driver_complete_order(request):
    # Get token
    access_token = AccessToken.objects.get(token=request.POST.get("access_token"),
                                           expires__gt=timezone.now())

    driver = access_token.user.driver

    order = Order.objects.get(id=request.POST["order_id"], driver=driver)
    order.status = Order.DELIVERED
    order.save()

    return JsonResponse({"status": "success"})


# GET params: access_token
def driver_get_revenue(request):
    access_token = AccessToken.objects.get(token=request.GET.get("access_token"),
                                           expires__gt=timezone.now())

    driver = access_token.user.driver

    from datetime import timedelta

    revenue = {}
    today = timezone.now()
    current_weekdays = [today + timedelta(days=i) for i in range(0 - today.weekday(), 7 - today.weekday())]

    for day in current_weekdays:
        orders = Order.objects.filter(
            driver=driver,
            status=Order.DELIVERED,
            created_at__year=day.year,
            created_at__month=day.month,
            created_at__day=day.day
        )

        revenue[day.strftime("%a")] = sum(order.total for order in orders)

    return JsonResponse({"revenue": revenue})


# POST - params: access_token, "lat,lng"
@csrf_exempt
def driver_update_location(request):
    if request.method == "POST":
        access_token = AccessToken.objects.get(token=request.POST.get("access_token"),
                                               expires__gt=timezone.now())

        driver = access_token.user.driver

        # Set location string => database
        driver.location = request.POST["location"]
        driver.save()

        return JsonResponse({"status": "success"})


class ReviewAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def get_queryset(self):
        return self.queryset.filter(chef__user=self.request.user)


class ChefContactInfoAPIView(generics.RetrieveAPIView):
    serializer_class = ChefContactSerializer
    permission_classes = []
    queryset = Chef.objects.all()


class ChefBioAPIView(generics.RetrieveAPIView):
    serializer_class = ChefBioSerializer
    permission_classes = []
    queryset = Chef.objects.all()


class ChefAvgRatingAPIView(generics.RetrieveAPIView):
    serializer_class = ChefAvgRatingSerializer
    permission_classes = []
    queryset = Review.objects.all()

    def get(self, request, *args, **kwargs):
        qset = self.queryset.filter(chef_id=self.kwargs['pk'])
        if qset.count() < 1:
            return Response({'message':'No review found'}, status=status.HTTP_404_NOT_FOUND)
        count = 0
        for x in qset:
            count = count + x.rating
        output = {'rating': count / qset.count(), 'number_of_reviews': qset.count()}
        return Response(ChefAvgRatingSerializer(output).data)


def get_or_create_customer(email, token):
    stripe.api_key = settings.STRIPE_API_KEY
    connected_customers = stripe.Customer.list()
    for customer in connected_customers:
        if customer.email == email:
            print(f'{email} found')
            return customer
            print(f'{email} created')
            return stripe.Customer.create(
                email=email,
                source=token,
            )
