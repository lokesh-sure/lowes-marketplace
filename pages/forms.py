from django import forms
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name", "category", "brand", "price", "description", "stock")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "price": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"min": "0", "step": "1"}),
        }


class ProductImageForm(forms.Form):
    image = forms.ImageField(required=False, help_text="Optional. Choose one product image.")


class CustomerEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
