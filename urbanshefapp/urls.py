"""urbanshefapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from urbanshef import views, apis
from django.contrib.auth import views as auth_views

from django.conf.urls.static import static
from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="Urbanshef API",
        default_version='1.0',
        description="Urbanshef API Documentation",
        terms_of_service="https://www.urbanshef.com/privacy/",
        contact=openapi.Contact(email="developers@urbanshef.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/users/', views.BrowseUsers, name='browse-user'),
    path('', views.index, name='home'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('food-safety/', views.food_safety, name='food-safety'),
    path('report-bugs/', views.report_bugs, name='report-bugs'),
    path('', include('urbanshef.urls')),

    # Chef
    path('chef/login/', auth_views.LoginView.as_view(template_name='chef/login.html'), name='chef-login'),
    path('chef/logout/', auth_views.LogoutView.as_view(next_page='/'), name='chef-logout'),
    path('chef/sign-up/', views.chef_sign_up, name='chef-sign-up'),
    path('chef/reset_password/', auth_views.PasswordResetView.as_view(template_name="chef/password_reset.html"),
         name="reset_password"),

    path('chef/reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name="chef/password_reset_sent.html"),
         name="password_reset_done"),

    path('chef/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="chef/password_reset_form.html"),
         name="password_reset_confirm"),

    path('chef/reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="chef/password_reset_done.html"),
         name="password_reset_complete"),

    path('chef/', views.chef_home, name='chef-home'),

    # Manage availablity
    path('updatechefavailability/', views.update_availability, name='update-availability'),
    path('checkavailability/', views.check_availability, name='check-availability'),

    path('chef/account/', views.chef_account, name='chef-account'),
    path('chef/meal/', views.chef_meal, name='chef-meal'),
    path('chef/meal/add/', views.chef_add_meal, name='chef-add-meal'),
    path('chef/meal/edit/<int:meal_id>/', views.chef_edit_meal, name='chef-edit-meal'),
    path('chef/order/', views.chef_order, name='chef-order'),
    path('chef/report/', views.chef_report, name='chef-report'),
    path('chef/review/', views.review, name='chef-review'),
    path('chef/review/reply/<int:review_id>', views.reply_to_review, name='chef-reply-review'),

    # # Stripe Connect
    # path('authorize/', StripeAuthorizeView.as_view(), name='authorize'),
    # path('oauth/callback/', StripeAuthorizeCallbackView.as_view(), name='authorize_callback'),

    # Sign In/ Sign Up/ Sign Out
    path('api/social/', include('drf_social_oauth2.urls', namespace='drf')),

    # /convert-token (sign in/ sign up)
    # /revoke-token (sign out)
    path('api/chef/order/notification/<int:last_request_time>/', apis.chef_order_notification),

    # # APIs for CUSTOMERS
    path('api/customer/chefs/', apis.CustomerGetChefs.as_view()),
    path('api/customer/meals/<int:chef_id>/', apis.CustomerGetMeals.as_view()),
    path('api/customer/order/add/', apis.customer_add_order),
    path('api/customer/order/latest/', apis.customer_get_latest_order),
    path('api/customer/driver/location/', apis.customer_driver_location),
    #
    #
    # # APIs for DRIVERS
    path('api/driver/orders/ready/', apis.driver_get_ready_orders),
    path('api/driver/order/pick/', apis.driver_pick_order),
    path('api/driver/order/latest/', apis.driver_get_latest_order),
    path('api/driver/order/complete/', apis.driver_complete_order),
    path('api/driver/revenue/', apis.driver_get_revenue),
    path('api/driver/location/update/', apis.driver_update_location),

    # Review API
    path('api/review/', apis.ReviewAPIView.as_view()),

    # Chef contact
    path('api/chef/contact/<pk>/', apis.ChefContactInfoAPIView.as_view()),

    # Chef Bio
    path('api/chef/bio/<pk>/', apis.ChefBioAPIView.as_view()),

    # Chef average review
    path('api/chef/review/<pk>/', apis.ChefAvgRatingAPIView.as_view()),

    path('doc/', schema_view.with_ui('swagger', cache_timeout=-25), name='schema-swagger-ui')

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'urbanshef.views.error_404_view'
