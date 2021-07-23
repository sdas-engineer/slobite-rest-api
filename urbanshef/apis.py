import json

import requests
import stripe
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.models import AccessToken
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from twilio.rest import Client

from urbanshef.models import Chef, Meal, Order, OrderDetails, Review, Coupon, Customer
from urbanshef.serializers import ChefSerializer, \
    MealSerializer, \
    OrderSerializer, ReviewSerializer, ChefContactSerializer, ChefBioSerializer, ChefAvgRatingSerializer, \
    OrderCreateSerializer, MealAllergensSerializer, CouponSerializer, PaymentMethodSerializer, CheckPaymentSerializer, \
    PaymentIntentSerializer, PaymentIntentConfirmSerializer, PaymentIntentCancelSerializer, \
    PaymentIntentModifySerializer
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
        """
        customer/chefs/?cuisine=
        """
        c = self.get_queryset()
        if request.GET.get('cuisine'):
            c = c.filter(cuisine=request.GET.get('cuisine'))
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


class PaymentSheet(generics.CreateAPIView):
    serializer_class = PaymentIntentSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            pass
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        try:
            access_token = AccessToken.objects.get(token=request.POST.get("access_token"),
                                                   expires__gt=timezone.now())

            customer_user = access_token.user
        except:
            return Response({'error': 'Invalid customer'}, status.HTTP_400_BAD_REQUEST)
        try:
            customer = stripe.Customer.retrieve(id=customer_user.customer.stripe_id)
        except:
            customer = stripe.Customer.create()
            c = Customer.objects.get(user=customer_user)
            c.stripe_id = customer.id
            c.save()
        ephemeralKey = stripe.EphemeralKey.create(customer=customer.id, stripe_version='2020-08-27')
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=request.POST['amount'],
                currency=request.POST['currency'],
                confirm=False,
                receipt_email=customer_user.email
            )
            return Response({'customer': customer, 'ephemeralKey': ephemeralKey, 'payment_intent': payment_intent},
                            status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': 'Invalid amount or currency'}, status.HTTP_400_BAD_REQUEST)


class PaymentMethodCreate(generics.CreateAPIView):
    serializer_class = PaymentMethodSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            pass
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        try:
            s = stripe.PaymentMethod.create(
                type=request.POST['type'],
                card={
                    "number": request.POST['card_number'],
                    "exp_month": request.POST['exp_month'],
                    "exp_year": request.POST['exp_year'],
                    "cvc": request.POST['cvc']
                }
            )
            return Response(s, status.HTTP_200_OK)
        except:
            return Response({'message': 'Invalid card information'}, status.HTTP_400_BAD_REQUEST)


class PaymentIntentCreate(generics.CreateAPIView):
    serializer_class = PaymentIntentSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            pass
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        amount = request.POST.get("amount")
        currency = request.POST.get('currency')
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                confirm=False
            )
            return Response(payment_intent, status.HTTP_200_OK)
        except:
            return Response({'message': 'Invalid amount or currency'}, status.HTTP_400_BAD_REQUEST)


class PaymentIntentModify(generics.CreateAPIView):
    serializer_class = PaymentIntentModifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            pass
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        pi = request.POST.get("id")
        payment_method = request.POST.get('payment_method')
        try:
            payment_intent = stripe.PaymentIntent.modify(
                pi,
                payment_method=payment_method
            )
            return Response(payment_intent, status.HTTP_200_OK)
        except:
            return Response({'message': 'Invalid payment ID or method. Try again'}, status.HTTP_400_BAD_REQUEST)


class PaymentIntentCheck(generics.CreateAPIView):
    serializer_class = CheckPaymentSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            pass
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        intent_id = request.POST['id']
        try:
            return Response(stripe.PaymentIntent.retrieve(intent_id), status.HTTP_200_OK)
        except:
            return Response({'message': 'Invalid payment id'}, status.HTTP_400_BAD_REQUEST)


class PaymentIntentConfirm(generics.CreateAPIView):
    serializer_class = PaymentIntentConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            pass
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        try:
            c = stripe.PaymentIntent.confirm(
                request.POST['id'],
                payment_method=request.POST['payment_method'],
            )
            return Response(c, status.HTTP_200_OK)
        except:
            return Response({'status': 'This payment might be canceled or already confirmed'},
                            status.HTTP_400_BAD_REQUEST)


class PaymentIntentCancel(generics.CreateAPIView):
    serializer_class = PaymentIntentCancelSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            pass
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        try:
            cancel = stripe.PaymentIntent.cancel(request.POST['id'])
            return Response(cancel, status.HTTP_200_OK)
        except:
            return Response({'status': 'This payment might be canceled or already confirmed'},
                            status.HTTP_400_BAD_REQUEST)


class CustomerAddAPIView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = []
    authentication_classes = []
    queryset = Order.objects.all()
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

    def post(self, request, *args, **kwargs):
        try:
            access_token = AccessToken.objects.get(token=request.POST.get("access_token"),
                                                   expires__gt=timezone.now())

            customer = access_token.user.customer

            # customer = Customer.objects.get(id=request.POST.get('access_token'))
        except Exception:
            return Response({"status": "failed", "error": "Invalid customer."})

        # Get Delivery Charge
        if not request.POST.get('delivery_charge'):
            delivery_charge = 3.0
        else:
            delivery_charge = float(request.POST.get("delivery_charge"))

        # Check whether customer has any order that is not delivered
        if Order.objects.filter(customer=customer).exclude(status=Order.DELIVERED):
            return Response({"status": "failed", "error": "Your last order must be completed."})

        # Check Address
        if not request.POST.get("customer_street_address"):
            return Response({"status": "failed", "error": "Address is required."})

        # Check Flat
        if not request.POST.get("customer_flat_number"):
            return Response({"status": "failed", "error": "Flat Number is required."})

        # Check Payment ID
        if not request.POST.get("payment_id"):
            return Response({"status": "failed", "error": "Payment ID is required."})

        # Check Phone
        if not request.POST.get("phone"):
            return Response({"status": "failed", "error": "Phone is required."})
        # Check the coupon
        discountParcent = 0
        cInstance = None
        if request.POST.get('coupon'):
            c = Coupon.objects.filter(code=request.POST.get('coupon'), active=True, valid_from__lte=timezone.now(),
                                      valid_to__gte=timezone.now())
            if len(c):
                cInstance = c.first()
                discountParcent = cInstance.discount
        # Get Order Details
        order_details = json.loads(request.POST["order_details"])

        order_total = 0
        for meal in order_details:
            order_total += Meal.objects.get(id=meal["meal_id"]).price * meal["quantity"]

        if not request.POST.get('service_charge'):
            service_charge = float(order_total + delivery_charge) * 0.1
        else:
            service_charge = float(request.POST.get("service_charge"))

        order_total_including_charge = float(order_total) + float(delivery_charge) + service_charge
        discountedAmount = 0
        if discountParcent != 0:
            discountedAmount = order_total_including_charge * (discountParcent / 100)
        order_total_including_charge = order_total_including_charge - discountedAmount
        if len(order_details) > 0:
            # Step 2 - Create an Order
            order = Order.objects.create(
                customer=customer,
                chef_id=request.POST["chef_id"],
                total=order_total_including_charge,
                status=Order.COOKING,
                customer_street_address=request.POST["customer_street_address"],
                customer_flat_number=request.POST["customer_flat_number"],
                phone=request.POST["phone"],
                delivery_charge=delivery_charge,
                service_charge=service_charge,
                delivery_instructions=request.POST.get('delivery_instructions'),
                coupon=cInstance,
                pre_order=request.POST.get('pre_order'),
                discount_amount=discountedAmount,
                payment_id=request.POST['payment_id']
            )
            # Step 3 - Create Order details
            for meal in order_details:
                OrderDetails.objects.create(
                    order=order,
                    meal_id=meal["meal_id"],
                    quantity=meal["quantity"],
                    sub_total=Meal.objects.get(id=meal["meal_id"]).price * meal["quantity"],
                    # tax=0,
                    # service_charge=0,
                    # customer_street_address=request.POST["customer_street_address"],
                    # customer_flat_number=request.POST["customer_flat_number"],

                )
            message_to_broadcast = (
                "Hello chef! You have a new order. View your Urbanshef dashboard to fulfill the order!")
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            try:
                client.messages.create(to=order.chef.phone, from_=settings.TWILIO_NUMBER, body=message_to_broadcast)
            except:
                print('Unable to send message to ' + order.chef.phone)
            send_mail('Urbanshef: New Order Alert',
                      'Hello chef! You have a new order. View your Urbanshef dashboard to fulfill the order!',
                      'no-reply@urbanshef.com',
                      [order.chef.user.email], fail_silently=False)
            return Response({"status": "success"})


class customer_get_latest_order(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        try:
            access_token = AccessToken.objects.get(token=request.GET["access_token"],
                                                   expires__gt=timezone.now())
            customer = access_token.user.customer
            # customer = Customer.objects.get(id=request.GET.get('access_token'))
        except:
            return Response({'status': 'failed', 'error': 'Invalid customer'})
        order = OrderSerializer(Order.objects.filter(customer=customer).last(), many=False).data
        return Response(order, status.HTTP_200_OK)


class customer_driver_location(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        try:
            access_token = AccessToken.objects.get(token=request.GET.get("access_token"),
                                                   expires__gt=timezone.now())

            customer = access_token.user.customer
        except:
            return Response({'status': 'failed', 'error': 'Invalid customer'})

        # Get driver's location related to this customer's current order.
        current_order = Order.objects.filter(customer=customer, status=Order.DELIVERED).last()
        location = current_order.driver.location

        return Response({"location": location})


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

class driver_get_ready_orders(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        orders = OrderSerializer(
            Order.objects.filter(status=Order.READY).order_by("-id"),
            many=True
        ).data

        return Response({"orders": orders})


@csrf_exempt
# POST
# params: access_token, order_id
def driver_pick_order(request):
    if request.method == "POST":
        try:
            # Get token
            access_token = AccessToken.objects.get(token=request.POST.get("access_token"),
                                                   expires__gt=timezone.now())

            # Get Driver
            driver = access_token.user.driver
        except:
            return JsonResponse({'status': 'failed', 'error': 'Invalid user'})

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
    try:
        access_token = AccessToken.objects.get(token=request.GET.get("access_token"),
                                               expires__gt=timezone.now())

        driver = access_token.user.driver
    except:
        return JsonResponse({'status': 'failed', 'error': 'Invalid user'})
    order = OrderSerializer(
        Order.objects.filter(driver=driver).order_by("picked_at").last()
    ).data

    return JsonResponse({"order": order})


# POST params: access_token, order_id
@csrf_exempt
def driver_complete_order(request):
    # Get token
    try:
        access_token = AccessToken.objects.get(token=request.POST.get("access_token"),
                                               expires__gt=timezone.now())

        driver = access_token.user.driver
        # driver=Driver.objects.get(id=request.POST.get("access_token"))
    except:
        return JsonResponse({'status': 'failed', 'error': 'Invalid user'})
    try:
        order = Order.objects.get(id=request.POST["order_id"], driver=driver)
        order.status = Order.DELIVERED
        order.save()

        return JsonResponse({"status": "success"})
    except:
        return JsonResponse({'status': 'failed', 'error': 'Invalid order'})


# GET params: access_token
def driver_get_revenue(request):
    try:
        access_token = AccessToken.objects.get(token=request.GET.get("access_token"),
                                               expires__gt=timezone.now())

        driver = access_token.user.driver
    except:
        return JsonResponse({'status': 'failed', 'error': 'Invalid user'})

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
        try:
            access_token = AccessToken.objects.get(token=request.POST.get("access_token"),
                                                   expires__gt=timezone.now())

            driver = access_token.user.driver
            driver.location = request.POST["location"]
            driver.save()

            return JsonResponse({"status": "success"})
        except:
            return JsonResponse({'status': 'failed', 'error': 'Invalid user'})


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
            return Response({'message': 'No review found'}, status=status.HTTP_404_NOT_FOUND)
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


class MealAllergens(generics.RetrieveAPIView):
    serializer_class = [MealAllergensSerializer]
    queryset = Meal.objects.all()

    def get(self, request, *args, **kwargs):
        m = Meal.objects.filter(Q(id=self.kwargs['meal_id']))
        if m.exists():
            return Response({"allergens": m[0].allergen}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No meal found"}, status=status.HTTP_404_NOT_FOUND)


class ApplyCoupon(generics.CreateAPIView):
    serializer_class = CouponSerializer
    queryset = Coupon.objects.all()

    def post(self, request, *args, **kwargs):
        c = Coupon.objects.filter(Q(code=request.data['code']))
        if c.exists():
            return Response(CouponSerializer(c.first(), many=False).data)
        return Response({'error': 'Invalid coupon code'}, status=status.HTTP_406_NOT_ACCEPTABLE)


class ShefUKFoodRating(APIView):
    def get(self, request, chef_id):
        try:
            chef = Chef.objects.get(id=chef_id)
        except:
            return Response({'status': 'Invalid chef id'}, status.HTTP_400_BAD_REQUEST)
        if chef.chef_street_address.place == '':
            return Response({'status': 'Chef doesn\'t have street address'}, status.HTTP_400_BAD_REQUEST)
        response = requests.get(
            'http://ratings.food.gov.uk/search/' + chef.name + '/' + chef.chef_street_address.place.split(',')[
                0] + '/json')
        json_data = response.json()
        if int(json_data['FHRSEstablishment']['Header']['ItemCount']) == 1:
            dObject = json_data['FHRSEstablishment']['EstablishmentCollection']['EstablishmentDetail']
            if dObject['RatingValue'] == 'Awaiting Inspection':
                imgUrl = staticfiles_storage.url('img/uk_food_rating/large/326ppi/fhis_awaiting_inspection.jpg')
            elif dObject['RatingValue'] == 'AwaitingInspection':
                imgUrl = staticfiles_storage.url('img/uk_food_rating/large/326ppi/fhrs_awaitinginspection_en-gb.jpg')
            elif dObject['RatingValue'] == '5':
                imgUrl = staticfiles_storage.url('img/uk_food_rating/large/326ppi/fhrs_5_en-gb.jpg')
            elif dObject['RatingValue'] == '4':
                imgUrl = staticfiles_storage.url('img/uk_food_rating/large/326ppi/fhrs_4_en-gb.jpg')
            elif dObject['RatingValue'] == '3':
                imgUrl = staticfiles_storage.url('img/uk_food_rating/large/326ppi/fhrs_3_en-gb.jpg')
            elif dObject['RatingValue'] == '2':
                imgUrl = staticfiles_storage.url('img/uk_food_rating/large/326ppi/fhrs_2_en-gb.jpg')
            elif dObject['RatingValue'] == '1':
                imgUrl = staticfiles_storage.url('img/uk_food_rating/large/326ppi/fhrs_1_en-gb.jpg')
            elif dObject['RatingValue'] == '0':
                imgUrl = staticfiles_storage.url('img/uk_food_rating/large/326ppi/fhrs_0_en-gb.jpg')
            elif dObject['RatingValue'] == 'Exempt':
                imgUrl = staticfiles_storage.url('img/uk_food_rating/large/326ppi/fhrs_exempt_en-gb.jpg')
            elif dObject['RatingValue'] == 'Pass':
                imgUrl = staticfiles_storage.url('img/uk_food_rating/large/326ppi/fhis_pass.jpg')
            else:
                imgUrl = dObject['RatingValue']
            return Response({'url': imgUrl})
        else:
            return Response({'status': 'No rating found'}, status.HTTP_404_NOT_FOUND)
