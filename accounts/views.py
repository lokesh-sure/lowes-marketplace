import random
import string

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import UserProfile


def generate_captcha():
    characters = string.ascii_uppercase + string.digits
    return "".join(random.choices(characters, k=6))


def register_view(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        captcha_input = request.POST.get("captcha", "").strip().upper()

        captcha_code = request.session.get("register_captcha")

        if not captcha_code or captcha_input != captcha_code:

            messages.error(
                request,
                "Invalid CAPTCHA. Please try again."
            )

            request.session["register_captcha"] = generate_captcha()

            return render(
                request,
                "accounts/register.html",
                {
                    "captcha_code": request.session["register_captcha"]
                }
            )

        try:
            validate_password(password, user=None)

        except ValidationError as e:

            for error in e.messages:
                messages.error(request, error)

            request.session["register_captcha"] = generate_captcha()

            return render(
                request,
                "accounts/register.html",
                {
                    "captcha_code": request.session["register_captcha"]
                }
            )

        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "Username already exists."
            )

            request.session["register_captcha"] = generate_captcha()

            return render(
                request,
                "accounts/register.html",
                {
                    "captcha_code": request.session["register_captcha"]
                }
            )

        if User.objects.filter(email=email).exists():

            messages.error(
                request,
                "Email already registered."
            )

            request.session["register_captcha"] = generate_captcha()

            return render(
                request,
                "accounts/register.html",
                {
                    "captcha_code": request.session["register_captcha"]
                }
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        UserProfile.objects.create(
            user=user,
            full_name=username,
            email=email,
            phone=""
        )

        request.session.pop(
            "register_captcha",
            None
        )

        messages.success(
            request,
            "Registration successful. Please login."
        )

        return redirect("accounts:login")

    captcha_code = generate_captcha()

    request.session["register_captcha"] = captcha_code

    return render(
        request,
        "accounts/register.html",
        {
            "captcha_code": captcha_code
        }
    )


def login_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        if not username or not password:

            messages.error(
                request,
                "Username and password are required."
            )

            return render(
                request,
                "accounts/login.html"
            )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_active:

            login(
                request,
                user
            )

            messages.success(
                request,
                f"Welcome, {user.username}!"
            )

            return redirect("/cart/")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "accounts/login.html"
    )


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
        ).filter(
            email=email
        ).exists():

            messages.error(
                request,
                "This email is already being used by another account."
            )

            return redirect("accounts:profile")

        if UserProfile.objects.exclude(
            user=request.user
        ).filter(
            email=email
        ).exists():

            messages.error(
                request,
                "This email is already being used by another profile."
            )

            return redirect("accounts:profile")

        request.user.email = email

        request.user.save(
            update_fields=["email"]
        )

        profile.full_name = full_name
        profile.email = email
        profile.phone = phone

        profile.save()

        messages.success(
            request,
            "Profile updated successfully."
        )

        return redirect("accounts:profile")

    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile
        }
    )


def logout_view(request):

    logout(request)

    messages.success(
        request,
        "Logged out successfully."
    )

    return redirect("accounts:login")