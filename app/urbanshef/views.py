import urllib
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from urbanshef.forms import UserForm, ChefForm, UserFormForEdit, MealForm
from django.contrib.auth import authenticate, login

from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse, Http404

from django.views import View
from django.conf import settings

from .models import Chef, Review, Customer

from django.contrib.auth.models import User
from urbanshef.models import Meal, Order, Driver

from django.db.models import Sum, Count, Case, When


# Create your views here.
def index(request):
    return render(request, 'home.html')

def privacy(request):
    return render(request, 'privacy.html')

def terms(request):
    return render(request, 'terms.html')

def food_safety(request):
    return render(request, 'food-safety.html')

def report_bugs(request):
    return render(request, 'report-bugs.html')

def home(request):
    return redirect(chef_home)


@login_required(login_url='/chef/login/')
def chef_home(request):
    return redirect(chef_order)


@login_required(login_url='/chef/login/')
def chef_account(request):
    loadChefAvailability(request)
    user_form = UserFormForEdit(instance=request.user)
    chef = Chef.objects.get(user=request.user)
    chef_form = ChefForm(instance=chef)

    if request.method == "POST":
        user_form = UserFormForEdit(request.POST, instance=request.user)
        chef_form = ChefForm(request.POST, request.FILES, instance=request.user.chef)
        if user_form.is_valid() and chef_form.is_valid():
            user_form.save()
            chef_form.save()
        chef = Chef.objects.get(user=request.user)

    return render(request, 'chef/account.html', {
        "user_form": user_form,
        "chef_form": chef_form,
        "chef": chef
    })


@login_required(login_url='/chef/login/')
def chef_meal(request):
    loadChefAvailability(request)
    meals = Meal.objects.filter(chef=request.user.chef).order_by("-id")
    return render(request, 'chef/meal.html', {"meals": meals})


@login_required(login_url='/chef/login/')
def chef_add_meal(request):
    loadChefAvailability(request)
    form = MealForm()

    if request.method == "POST":
        form = MealForm(request.POST, request.FILES)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.chef = request.user.chef
            meal.save()
            return redirect(chef_meal)

    return render(request, 'chef/add_meal.html', {
        "form": form
    })


@login_required(login_url='/chef/login/')
def chef_edit_meal(request, meal_id):
    loadChefAvailability(request)
    form = MealForm(instance=Meal.objects.get(id=meal_id))
    inst=Meal.objects.get(id=meal_id)

    if request.method == "POST":
        form = MealForm(request.POST, request.FILES, instance=Meal.objects.get(id=meal_id))
        if form.is_valid():
            form.save()
            return redirect(chef_meal)

    return render(request, 'chef/edit_meal.html', {
        "form": form, "meal":inst
    })


@login_required(login_url='/chef/login/')
def chef_order(request):
    loadChefAvailability(request)
    if request.method == "POST":
        order = Order.objects.get(id=request.POST["id"], chef=request.user.chef)

        if order.status == Order.COOKING:
            order.status = Order.READY
            order.save()

    orders = Order.objects.filter(chef=request.user.chef).order_by("-id")
    return render(request, 'chef/order.html', {"orders": orders})


@login_required(login_url='/chef/login/')
def chef_report(request):
    loadChefAvailability(request)
    # Calculate revenue and number of order by current week
    from datetime import datetime, timedelta

    revenue = []
    orders = []

    # Calculate weekdays
    today = datetime.now()
    current_weekdays = [today + timedelta(days=i) for i in range(0 - today.weekday(), 7 - today.weekday())]

    for day in current_weekdays:
        delivered_orders = Order.objects.filter(
            chef=request.user.chef,
            status=Order.DELIVERED,
            created_at__year=day.year,
            created_at__month=day.month,
            created_at__day=day.day
        )
        revenue.append(sum(order.total for order in delivered_orders))
        orders.append(delivered_orders.count())

    # Top 3 Meals
    top3_meals = Meal.objects.filter(chef=request.user.chef) \
                     .annotate(total_order=Sum('orderdetails__quantity')) \
                     .order_by("-total_order")[:3]

    meal = {
        "labels": [meal.name for meal in top3_meals],
        "data": [meal.total_order or 0 for meal in top3_meals]
    }

    # Top 3 Drivers
    top3_drivers = Driver.objects.annotate(
        total_order=Count(
            Case(
                When(order__chef=request.user.chef, then=1)
            )
        )
    ).order_by("-total_order")[:3]

    driver = {
        "labels": [driver.user.get_full_name() for driver in top3_drivers],
        "data": [driver.total_order for driver in top3_drivers]
    }

    return render(request, 'chef/report.html', {
        "revenue": revenue,
        "orders": orders,
        "meal": meal,
        "driver": driver
    })


@login_required(login_url='/chef/login/')
def review(request):
    loadChefAvailability(request)
    rateList = [1, 2, 3, 4, 5]
    getReview = Review.objects.filter(chef__user=request.user)
    return render(request, 'chef/review.html', {"reviews": getReview, "starList": rateList})


@login_required(login_url='/chef/login/')
def reply_to_review(request, review_id):
    loadChefAvailability(request)
    try:
        review = get_object_or_404(Review, id=review_id)
        if request.POST:
            review.reply = request.POST.get('reply')
            review.save()
            return redirect('chef-review')
        return render(request, 'chef/reply.html', {'review': review})
    except:
        return redirect('chef-review')


@login_required(login_url='/chef/login/')
def update_availability(request):
    chef = Chef.objects.get(user=request.user)
    if chef.available:
        chef.available = False
    else:
        chef.available = True
    request.session['available'] = chef.available
    chef.save()
    data = {'status': 'Saved successfully'}
    return JsonResponse(data)


@login_required(login_url='/chef/login/')
def check_availability(request):
    chef = Chef.objects.get(user=request.user)
    return JsonResponse({"availability": chef.available, "disabled_by_admin": chef.disabled_by_admin})


def chef_sign_up(request):
    user_form = UserForm()

    if request.method == "POST":
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            new_user = User.objects.create_user(**user_form.cleaned_data)
            Chef.objects.create(user=new_user, name=request.POST.get('kitchen_name'))
            login(request, authenticate(
                username=user_form.cleaned_data["username"],
                password=user_form.cleaned_data["password"]
            ))
            return redirect(chef_account)

    return render(request, "chef/sign_up.html", {
        "user_form": user_form
    })


class StripeAuthorizeView(View):

    def get(self, request):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        url = 'https://connect.stripe.com/oauth/authorize'
        params = {
            'response_type': 'code',
            'scope': 'read_write',
            'client_id': settings.STRIPE_CONNECT_CLIENT_ID,
            'redirect_uri': f'https://www.urbanshef.com/oauth/callback'
        }
        url = f'{url}?{urllib.parse.urlencode(params)}'
        return redirect(url)


class StripeAuthorizeCallbackView(View):

    def get(self, request):
        code = request.GET.get('code')
        if code:
            data = {
                'client_secret': settings.STRIPE_API_KEY,
                'grant_type': 'authorization_code',
                'client_id': settings.STRIPE_CONNECT_CLIENT_ID,
                'code': code
            }
            url = 'https://connect.stripe.com/oauth/token'
            resp = requests.post(url, params=data)
            # add stripe info to the chef
            stripe_user_id = resp.json()['stripe_user_id']
            stripe_access_token = resp.json()['access_token']
            chef = Chef.objects.filter(user_id=self.request.user.id).first()
            chef.stripe_access_token = stripe_access_token
            chef.stripe_user_id = stripe_user_id
            chef.save()
        url = reverse('chef-home')
        response = redirect(url)
        return response


# class MealChargeView(View):
#
#     def post(self, request, *args, **kwargs):
#         stripe.api_key = settings.STRIPE_SECRET_KEY
#         json_data = json.loads(request.body)
#         meal = Meal.objects.filter(id=json_data['meal_id']).first()
#         fee_percentage = .15 * int(meal.fee)
#         try:
#             customer = get_or_create_customer(
#                 self.request.user.email,
#                 json_data['token'],
#             )
#             charge = stripe.Charge.create(
#                 amount=json_data['amount'],
#                 currency='gbp',
#                 customer=customer.id,
#                 description=json_data['description'],
#                 destination={
#                     'amount': int(json_data['amount'] - (json_data['amount'] * fee_percentage)),
#                     'account': meal.chef.stripe_user_id,
#                 },
#             )
#             if charge:
#                 return JsonResponse({'status': 'success'}, status=202)
#         except stripe.error.StripeError as e:
#             return JsonResponse({'status': 'error'}, status=500)
def loadChefAvailability(request):
    user = Chef.objects.get(user_id=request.user.id)
    request.session['available'] = user.available


@login_required(login_url='/chef/login/')
def BrowseUsers(request):
    if request.user.is_superuser:
        if request.GET.get('type') is None:
            return redirect('/admin/users/?type=chef')
        if request.GET.get('type') == 'chef':
            user = Chef.objects.all()
        elif request.GET.get('type') == 'customer':
            user = Customer.objects.all()
        elif request.GET.get('type') == 'driver':
            user = Driver.objects.all()
        else:
            return redirect('/admin/users/?type=chef')
        context = {
            "users": user
        }
        print(user)
        return render(request, '_admin_users.html', context)
    else:
        return redirect(chef_home)

def error_404_view(request, exception):
    return render(request,'404.html')
