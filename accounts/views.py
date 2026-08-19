from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import UserProfile


def register_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("accounts:register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("accounts:register")

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

        messages.success(request, "Registration successful. Please login.")
        return redirect("accounts:login")

    return render(request, "accounts/register.html")


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect("/cart/")

        messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


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
        request.user.save(update_fields=["email"])

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