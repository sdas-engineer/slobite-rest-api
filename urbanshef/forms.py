from django import forms

from django.contrib.auth.models import User
from places.fields import PlacesField

from urbanshef.models import Chef, Meal, Review
from django.contrib.auth.forms import PasswordResetForm


class UserForm(forms.ModelForm):
    email = forms.CharField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ("username", "password", "first_name", "last_name", "email")


class UserFormForEdit(forms.ModelForm):
    email = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class ChefForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}))
    gender = forms.CharField(widget=forms.Select(attrs={'class': 'form-control'},
                                                 choices=(("Male", "Male"), ("Female", "Female"), ("Other", "Other"))))
    # Added on Demand
    delivery_time = forms.CharField(widget=forms.Select(attrs={'class': 'form-control'}, choices=(
        ('Pre-order', 'Pre-order'), ('30-60 min', '30-60 min'), ('60-120 min', '60-120 min'))))
    # ----------
    cuisine = forms.CharField(widget=forms.Select(attrs={'class': 'form-control'}, choices=(
        ("British", "British"), ("Chinese", "Chinese"), ("Japanese", "Japanese"), ("Indian", "Indian"),
        ("Italian", "Italian"), ("Pakistani", "Pakistani"), ("Middle East", "Middle East"), ("Nepalese", "Nepalese"),
        ("Mexican", "Mexican"), ("Korean", "Korean"), ("African", "African"), ("Mediterranean", "Mediterranean"),
        ("Caribbean", "Caribbean"), ("French", "French"), ("Latin American", "Latin American"), ("Spanish", "Spanish"),
        ("South East Asian", "South East Asian"), ("European", "European"))))

    class Meta:
        model = Chef
        fields = ("name", "phone", "chef_street_address", "chef_flat_number", "city", "postcode", "picture", "authorized_to_work_in_the_UK", 'date_of_birth', 'gender', 'bio',
                  'cuisine', 'delivery_time')


class MealForm(forms.ModelForm):
    data = [('Celery', 'Celery'), ('Gluten', 'Gluten'), ('Crustaceans', 'Crustaceans'), ('Eggs', 'Eggs'),
            ('Fish', 'Fish'), (
                'Lupin', 'Lupin'), ('Milk', 'Milk'), ('Molluscs', 'Molluscs'), ('Mustard', 'Mustard'),
            ('Peanuts', 'Peanuts'), (
                'Sesame', 'Sesame'), ('Soybeans', 'Soybeans'), ('Sulphur dioxide', 'Sulphur dioxide'),
            ('Sulphites', 'Sulphites'), (
                'Nuts', 'Nuts')]
    allergen = forms.MultipleChoiceField(
        required=False,
        disabled=False,
        initial=[],
        choices=[(i[0], i[0]) for i in data],
        widget=forms.CheckboxSelectMultiple
    )
    food_type = forms.CharField(widget=forms.Select(attrs={'class': 'form-control'}, choices=(
        ('Appetizer', 'Appetizer'), ('Main', 'Main'), ('Side', 'Side'), ('Dessert', 'Dessert'))))

    # Added On Demand
    spicy = forms.CharField(widget=forms.Select(attrs={'class': 'form-control'}, choices=(
        (None, '----'), ('Mild', 'Mild'), ('Medium', 'Medium'), ('Hot', 'Hot'), ('Extreme', 'Extreme'))),
                            required=False)
    diet = forms.CharField(widget=forms.Select(attrs={'class': 'form-control'}, choices=(
        (None, '----'), ('Vegan', 'Vegan'), ('Vegetarian', 'Vegetarian'))), required=False)

    # -------------------------
    cuisine = forms.CharField(widget=forms.Select(attrs={'class': 'form-control'}, choices=(
        ("British", "British"), ("Chinese", "Chinese"), ("Japanese", "Japanese"), ("Indian", "Indian"),
        ("Italian", "Italian"), ("Pakistani", "Pakistani"), ("Middle East", "Middle East"), ("Nepalese", "Nepalese"),
        ("Mexican", "Mexican"), ("Korean", "Korean"), ("African", "African"), ("Mediterranean", "Mediterranean"),
        ("Caribbean", "Caribbean"), ("French", "French"), ("Latin American", "Latin American"), ("Spanish", "Spanish"),
        ("South East Asian", "South East Asian"), ("European", "European"))))
    availability = forms.CharField(widget=forms.Select(attrs={'class': 'form-control'}, choices=(
        ('Available', 'Available'), ('Unavailable', 'Unavailable'))))

    class Meta:
        model = Meal
        fields = ['name', 'short_description', 'image', 'price', 'portion_size', 'food_type', 'spicy', 'diet',
                  'allergen', 'cuisine',
                  'availability']
        exclude = ("chef",)


class CustomPasswordResetForm(PasswordResetForm):

    def save(self, *args, **kwargs):
        kwargs['use_https'] = True
        super(CustomPasswordResetForm, self).save(*args, **kwargs)
