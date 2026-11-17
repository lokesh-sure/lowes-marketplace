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


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if isinstance(data, (list, tuple)):
            return [super(MultipleImageField, self).clean(item, initial) for item in data]
        if data:
            return [super().clean(data, initial)]
        if self.required:
            self.validate(None)
        return []


class SalePosterForm(forms.Form):
    posters = MultipleImageField(
        required=False,
        label="Poster images",
        help_text="Choose 1 to 3 images. Saving replaces the current homepage posters.",
        widget=MultipleFileInput(attrs={"accept": "image/jpeg,image/png,image/webp"}),
    )
    alt_text = forms.CharField(
        required=False,
        max_length=200,
        initial="Store sale poster",
        label="Image description",
        help_text="A short description for screen readers.",
    )

    def clean_posters(self):
        posters = self.cleaned_data["posters"]
        if len(posters) > 3:
            raise forms.ValidationError("Choose no more than 3 poster images.")

        allowed_types = {"image/jpeg", "image/png", "image/webp"}
        for poster in posters:
            if poster.size > 8 * 1024 * 1024:
                raise forms.ValidationError("Each poster must be 8 MB or smaller.")
            if getattr(poster, "content_type", "") not in allowed_types:
                raise forms.ValidationError("Use JPG, PNG, or WebP images only.")
            if getattr(getattr(poster, "image", None), "format", "") not in {"JPEG", "PNG", "WEBP"}:
                raise forms.ValidationError("Use JPG, PNG, or WebP images only.")
        return posters


class CustomerEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
