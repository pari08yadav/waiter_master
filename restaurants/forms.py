from django import forms
from django.forms import BooleanField, CharField

from shared.common.taxonomies import MenuType


class RestaurantForm(forms.Form):
    uid = CharField(required=False)
    name = CharField(max_length=512)


class CategoryForm(forms.Form):
    uid = CharField(required=False)
    name = CharField(max_length=512)

    def __init__(self, *args, restaurant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.restaurant = restaurant


class MenuItemForm(forms.Form):
    uid = CharField(required=False)
    name = CharField(max_length=512)
    menu_type = forms.ChoiceField(choices=MenuType.choices)
    available = BooleanField(required=False)
    half_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False, initial=0)
    full_price = forms.DecimalField(max_digits=10, decimal_places=2)
    description = forms.CharField(required=False, widget=forms.Textarea)
    ingredients = forms.CharField(required=False, widget=forms.Textarea)

    def __init__(self, *args, category=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = category

    def clean_half_price(self):
        return self.cleaned_data.get("half_price") or 0
