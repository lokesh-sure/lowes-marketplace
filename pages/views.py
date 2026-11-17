from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.mail import send_mail
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from products.models import Product, ProductImage, Category
from .forms import ProductForm, ProductImageForm, CustomerEditForm, SalePosterForm, CategoryImageForm, BrandLogoForm
from .models import SalePoster, StoreBranding

User = get_user_model()


def staff_required(view):
    return user_passes_test(
        lambda user: user.is_authenticated and user.is_active and user.is_staff,
        login_url="pages:admin_access",
    )(view)


def about(request):
    return render(request, "pages/about.html")


def privacy(request):
    return render(request, "pages/privacy.html")


def help_center(request):
    return render(request, "pages/help.html")


def admin_access(request):
    if request.user.is_authenticated and request.user.is_active and request.user.is_staff:
        return redirect("pages:admin_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_active and user.is_staff:
            login(request, user)
            return redirect("pages:admin_dashboard")

        messages.error(request, "Enter valid credentials for an active staff account.")

    return render(request, "pages/admin_access.html")


@staff_required
def admin_dashboard(request):
    return render(request, "pages/admin_dashboard.html", {
        "product_count": Product.objects.count(),
        "category_count": Category.objects.count(),
        "customer_count": User.objects.filter(is_staff=False).count(),
        "low_stock_count": Product.objects.filter(stock__lte=5).count(),
        "sale_poster_count": SalePoster.objects.count(),
    })


@staff_required
def admin_branding(request):
    branding = StoreBranding.objects.filter(pk=1).first()
    form = BrandLogoForm()
    if request.method == "POST":
        if request.POST.get("action") == "remove":
            if branding:
                branding.logo_data = None
                branding.logo_content_type = ""
                branding.save(update_fields=["logo_data", "logo_content_type", "updated_at"])
            messages.success(request, "The default PreciousCart logo is showing again.")
            return redirect("pages:admin_branding")

        form = BrandLogoForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data["image"]
            image_format = getattr(getattr(image, "image", None), "format", "")
            if branding is None:
                branding = StoreBranding(pk=1)
            branding.logo_data = image.read()
            branding.logo_content_type = {
                "JPEG": "image/jpeg",
                "PNG": "image/png",
                "WEBP": "image/webp",
            }[image_format]
            branding.save()
            messages.success(request, "The store logo was updated across the website.")
            return redirect("pages:admin_branding")

    return render(request, "pages/admin_branding.html", {"form": form, "branding": branding})


def brand_logo_image(request):
    branding = StoreBranding.objects.filter(pk=1).first()
    if not branding or not branding.logo_data or not branding.logo_content_type:
        raise Http404("No custom store logo is set.")
    response = HttpResponse(branding.logo_data, content_type=branding.logo_content_type)
    response["Cache-Control"] = "no-cache, max-age=0, must-revalidate"
    response["X-Content-Type-Options"] = "nosniff"
    return response


@staff_required
def admin_sale_posters(request):
    form = SalePosterForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and request.POST.get("action") == "clear":
        SalePoster.objects.all().delete()
        messages.success(request, "Homepage sale posters removed. The default banner is showing again.")
        return redirect("pages:admin_sale_posters")

    if request.method == "POST" and form.is_valid():
        uploaded_posters = form.cleaned_data["posters"]
        if uploaded_posters:
            alt_text = form.cleaned_data["alt_text"].strip() or "Store sale poster"
            current_count = SalePoster.objects.count()
            if current_count + len(uploaded_posters) > 3:
                if current_count >= 3:
                    form.add_error(
                        "posters",
                        "The homepage already has 3 posters. Remove all posters before adding a new set.",
                    )
                else:
                    remaining_slots = 3 - current_count
                    form.add_error(
                        "posters",
                        f"There are already {current_count} poster(s). Choose no more than {remaining_slots} more.",
                    )
            else:
                with transaction.atomic():
                    for position, upload in enumerate(uploaded_posters, start=current_count):
                        image_format = getattr(getattr(upload, "image", None), "format", "")
                        content_type = {
                            "JPEG": "image/jpeg",
                            "PNG": "image/png",
                            "WEBP": "image/webp",
                        }.get(image_format)
                        SalePoster.objects.create(
                            image_data=upload.read(),
                            image_content_type=content_type,
                            alt_text=alt_text,
                            position=position,
                        )
                messages.success(request, f"{len(uploaded_posters)} homepage poster(s) added.")
                return redirect("pages:admin_sale_posters")
        else:
            form.add_error("posters", "Choose at least one image to add to the current posters.")

    return render(request, "pages/admin_sale_posters.html", {
        "form": form,
        "posters": SalePoster.objects.all(),
    })


def sale_poster_image(request, poster_id):
    poster = get_object_or_404(SalePoster, pk=poster_id)
    response = HttpResponse(poster.image_data, content_type=poster.image_content_type)
    response["Cache-Control"] = "public, max-age=3600"
    response["X-Content-Type-Options"] = "nosniff"
    return response


@staff_required
def admin_category_images(request):
    categories = Category.objects.only("id", "name", "image_content_type").order_by("name")
    image_form = CategoryImageForm()

    if request.method == "POST":
        category = get_object_or_404(Category, pk=request.POST.get("category_id"))
        action = request.POST.get("action")
        if action == "remove":
            category.image_data = None
            category.image_content_type = ""
            category.save(update_fields=["image_data", "image_content_type"])
            messages.success(request, f"The {category.name} category image was removed.")
            return redirect("pages:admin_category_images")

        image_form = CategoryImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            image = image_form.cleaned_data["image"]
            image_format = getattr(getattr(image, "image", None), "format", "")
            category.image_data = image.read()
            category.image_content_type = {
                "JPEG": "image/jpeg",
                "PNG": "image/png",
                "WEBP": "image/webp",
            }[image_format]
            category.save(update_fields=["image_data", "image_content_type"])
            messages.success(request, f"The {category.name} category image was saved.")
            return redirect("pages:admin_category_images")

        return render(request, "pages/admin_category_images.html", {
            "categories": categories,
            "image_form": image_form,
            "error_category_id": category.id,
        })

    return render(request, "pages/admin_category_images.html", {
        "categories": categories,
        "image_form": image_form,
        "error_category_id": None,
    })


def category_image(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if not category.image_data or not category.image_content_type:
        raise Http404("This category does not have a custom image.")
    response = HttpResponse(category.image_data, content_type=category.image_content_type)
    response["Cache-Control"] = "public, max-age=3600"
    response["X-Content-Type-Options"] = "nosniff"
    return response


@staff_required
def admin_products(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.select_related("category").order_by("name")
    if query:
        products = products.filter(name__icontains=query)
    return render(request, "pages/admin_products.html", {"products": products, "query": query})


@staff_required
def admin_product_form(request, product_id=None):
    product = get_object_or_404(Product, pk=product_id) if product_id else None
    form = ProductForm(request.POST or None, instance=product)
    image_form = ProductImageForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid() and image_form.is_valid():
        saved_product = form.save()
        image = image_form.cleaned_data.get("image")
        if image:
            ProductImage.objects.create(product=saved_product, image=image)
        messages.success(request, "Product saved successfully.")
        return redirect("pages:admin_products")
    return render(request, "pages/admin_product_form.html", {
        "form": form, "image_form": image_form, "product": product,
    })


@staff_required
@require_POST
def admin_product_delete(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, "Product deleted.")
    return redirect("pages:admin_products")


@staff_required
def admin_customers(request):
    query = request.GET.get("q", "").strip()
    customers = User.objects.filter(is_staff=False).order_by("username")
    if query:
        from django.db.models import Q
        customers = customers.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
            | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )
    return render(request, "pages/admin_customers.html", {"customers": customers, "query": query})


@staff_required
def admin_customer_edit(request, user_id):
    customer = get_object_or_404(User, pk=user_id, is_staff=False)
    form = CustomerEditForm(request.POST or None, instance=customer)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Customer details updated.")
        return redirect("pages:admin_customers")
    return render(request, "pages/admin_customer_form.html", {"form": form, "customer": customer})


@staff_required
@require_POST
def admin_customer_toggle(request, user_id):
    customer = get_object_or_404(User, pk=user_id, is_staff=False)
    customer.is_active = not customer.is_active
    customer.save(update_fields=["is_active"])
    messages.success(request, "Customer account " + ("activated." if customer.is_active else "deactivated."))
    return redirect("pages:admin_customers")


def contact(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        body = request.POST.get("message", "").strip()

        if not full_name or not email or not body:
            messages.error(request, "Please fill in your name, email, and message.")
        else:
            try:
                send_mail(
                    subject=f"PreciousCart contact message from {full_name}",
                    message=f"Name: {full_name}\nEmail: {email}\nPhone: {phone}\n\n{body}",
                    from_email=None,
                    recipient_list=["support@marketnest.com"],
                    fail_silently=False,
                )
            except Exception:
                messages.error(request, "We could not submit your message. Please try again later.")
            else:
                messages.success(request, "Thank you. Your message has been submitted to PreciousCart support.")
                return redirect("pages:contact")

    return render(request, "pages/contact.html")


@login_required
def addresses(request):
    addresses = request.session.get("saved_addresses", [])
    edit_id = request.GET.get("edit")
    edit_address = next(
        (address for address in addresses if str(address.get("id")) == edit_id),
        None,
    )

    if request.method == "POST":
        action = request.POST.get("action")
        address_id = request.POST.get("address_id")

        if action == "delete":
            addresses = [item for item in addresses if str(item.get("id")) != address_id]
        elif action == "default":
            for item in addresses:
                item["is_default"] = str(item.get("id")) == address_id
        elif action in {"save", "add"}:
            values = {
                "label": request.POST.get("label", "").strip(),
                "full_name": request.POST.get("full_name", "").strip(),
                "line1": request.POST.get("line1", "").strip(),
                "city": request.POST.get("city", "").strip(),
                "state": request.POST.get("state", "").strip(),
                "pincode": request.POST.get("pincode", "").strip(),
                "phone": request.POST.get("phone", "").strip(),
            }
            if not all(values.values()):
                messages.error(request, "Please complete every address field.")
                return render(request, "pages/addresses.html", {
                    "addresses": addresses,
                    "edit_address": values,
                    "editing": action == "save",
                })

            if action == "save":
                target = next((item for item in addresses if str(item.get("id")) == address_id), None)
                if target:
                    target.update(values)
            else:
                new_id = max((int(item.get("id", 0)) for item in addresses), default=0) + 1
                values.update({"id": new_id, "is_default": not addresses})
                addresses.append(values)
        request.session["saved_addresses"] = addresses
        messages.success(request, "Address updated.")
        return redirect("saved_addresses")

    return render(request, "pages/addresses.html", {
        "addresses": addresses,
        "edit_address": edit_address,
        "editing": edit_address is not None,
    })
