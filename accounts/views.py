
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import UserProfile


def register_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        terms_accepted = request.POST.get("terms") == "accepted"
        form_context = {"full_name": full_name, "email": email}

        if not full_name or not email or not password or not confirm_password or not terms_accepted:
            messages.error(request, "Complete all fields and accept the Terms & Conditions.")
            return render(request, "accounts/register.html", form_context)
        if password != confirm_password:
            messages.error(request, "The passwords do not match.")
            return render(request, "accounts/register.html", form_context)
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "This email is already registered.")
            return render(request, "accounts/register.html", form_context)

        try:
            validate_password(password, user=None)
        except ValidationError as error:
            for message in error.messages:
                messages.error(request, message)
            return render(request, "accounts/register.html", form_context)

        base_username = slugify(email.split("@", 1)[0])[:140] or "customer"
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username[:130]}{suffix}"
            suffix += 1

        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, full_name=full_name, email=email, phone="")
        messages.success(request, "Registration successful. Please login.")
        return redirect("accounts:login")

    return render(request, "accounts/register.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        account = User.objects.filter(email__iexact=email).first() if email else None

        if not email or not password:
            messages.error(request, "Email and password are required.")
        elif account is None:
            messages.error(request, "Invalid email or password.")
        else:
            user = authenticate(request, username=account.username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                messages.success(request, f"Welcome, {user.username}!")
                return redirect("home")
            messages.error(request, "Invalid email or password.")

        return render(request, "accounts/login.html", {"email": email})

    return render(request, "accounts/login.html")

@login_required
def profile_dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "full_name": request.user.username,
            "email": request.user.email,
            "phone": "",
        },
    )
    return render(request, "accounts/profile.html", {"profile": profile})


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "full_name": request.user.username,
            "email": request.user.email,
            "phone": "",
        }
    )

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        if User.objects.exclude(
            id=request.user.id
        ).filter(email=email).exists():
            messages.error(
                request,
                "This email is already being used by another account."
            )
            return redirect("accounts:profile")

        if UserProfile.objects.exclude(
            user=request.user
        ).filter(email=email).exists():
            messages.error(
                request,
                "This email is already being used by another profile."
            )
            return redirect("accounts:profile")

        request.user.email = email
        request.user.save(update_fields=["email"])

        profile.full_name = full_name
        profile.email = email
        profile.phone = phone
        profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("accounts:profile")

    return render(
        request,
        "accounts/profile_edit.html",
        {"profile": profile}
    )


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("accounts:login")
