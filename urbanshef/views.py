import re
import urllib
from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum, Count, Case, When, Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View

from urbanshef.forms import ChefForm, CustomPasswordResetForm, MealForm, UserForm, UserFormForEdit
from urbanshef.models import Meal, Order, Driver
from .models import Chef, Review, Customer


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
            meal.price = float(meal.price) + (float(meal.price) * 0.2)
            meal.save()
            return redirect(chef_meal)

    return render(request, 'chef/add_meal.html', {
        "form": form
    })


@login_required(login_url='/chef/login/')
def chef_edit_meal(request, meal_id):
    loadChefAvailability(request)
    form = MealForm(instance=Meal.objects.get(id=meal_id))
    inst = Meal.objects.get(id=meal_id)

    if request.method == "POST":
        form = MealForm(request.POST, request.FILES, instance=Meal.objects.get(id=meal_id))
        if form.is_valid():
            instance = form.save(commit=False)
            if float(inst.price) != float(request.POST.get('price')):
                instance.price = float(request.POST.get('price')) + (float(request.POST.get('price')) * 0.2)
            instance.save()
            return redirect(chef_meal)

    return render(request, 'chef/edit_meal.html', {
        "form": form, "meal": inst
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
    if request.GET.get('filter'):
        if request.GET.get('filter') == '24_hours':
            orders = orders.filter(created_at__range=(datetime.now() - timedelta(hours=24), datetime.now()))
        if request.GET.get('filter') == '7_days':
            orders = orders.filter(created_at__range=(datetime.now() - timedelta(days=7), datetime.now()))
        if request.GET.get('filter') == '30_days':
            orders = orders.filter(created_at__range=(datetime.now() - timedelta(days=30), datetime.now()))
    page = request.GET.get('page', 1)
    paginator = Paginator(orders, 25)  # Show 25 contacts per page.

    try:
        p = paginator.page(page)
    except PageNotAnInteger:
        p = paginator.page(1)
    except EmptyPage:
        p = paginator.page(paginator.num_pages)
    return render(request, 'chef/order.html',
                  {"orders": p})


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
        user = User.objects.all()
        has_error = False
        if user.filter(Q(email=request.POST['email'])).exists():
            messages.error(request, 'Email already registered.')
            has_error = True
        if user.filter(Q(username=request.POST['username'])):
            messages.error(request, 'Username already registered.')
            has_error = True
        if len(request.POST['password']) < 8:
            messages.error(request, 'Password must be greater than 8 character')
            has_error = True
        if request.POST['password'].isdigit():
            messages.error(request, 'Password can\'t be entirely numeric')
            has_error = True
        if has_error:
            return redirect('chef-sign-up')
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            new_user = User.objects.create_user(**user_form.cleaned_data)
            Chef.objects.create(user=new_user, phone=request.POST.get('phone_number'),
                                agree_terms_and_condition=bool(request.POST.get('agree_terms_and_condition')))
            login(request, authenticate(
                username=user_form.cleaned_data["username"],
                password=user_form.cleaned_data["password"]
            ))
            return redirect('chef-onboarding-call')
        else:
            messages.error(request, 'Something went wrong. Try again')
            return redirect('chef-sign-up')

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
    return render(request, '404.html')


class LoginView(View):
    def get(self, request):
        return render(request, 'chef/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        isUsernameEmail = False
        emailRegex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
        if (re.search(emailRegex, username)):
            isUsernameEmail = True
        if isUsernameEmail:
            try:
                auth = authenticate(request, username=User.objects.get(email=username).username, password=password)
            except:
                messages.error(request, 'Invalid email address')
                return redirect('chef-login')
        else:
            auth = authenticate(request, username=username, password=password)
        if auth:
            login(request, auth)
            return redirect('chef-checklist')
        else:
            messages.error(request, 'Invalid credential provided')
            return redirect('chef-login')


class PasswordReset(View):
    def get(self, request):
        return render(request, 'chef/password_reset.html')

    def post(self, request):
        associated_users = User.objects.filter(Q(email=request.POST['email']))
        if associated_users.exists():
            subject = "Password Reset Requested"
            email_template_name = "chef/password_reset_subject.txt"
            user = User.objects.get(email=request.POST['email'])
            current_site = get_current_site(request)
            c = {
                "email": request.POST['email'],
                'domain': current_site.domain,
                'site_name': 'Website',
                "uid": urlsafe_base64_encode(force_bytes(user)),
                "user": user,
                'token': default_token_generator.make_token(user),
                'protocol': 'http',
            }
            email = render_to_string(email_template_name, c)
            send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
            return redirect('password_reset_done')
        return redirect('password_reset_done')


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm


class CheckListView(View):
    def get(self, request):
        return render(request, 'chef/checklist.html')

class BecomeAShef(View):
    def get(self, request):
        return render(request, 'chef/become_a_shef.html')
