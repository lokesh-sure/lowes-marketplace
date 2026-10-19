from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import redirect, render


def about(request):
    return render(request, "pages/about.html")


def privacy(request):
    return render(request, "pages/privacy.html")


def help_center(request):
    return render(request, "pages/help.html")


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
                    subject=f"MarketNest contact message from {full_name}",
                    message=f"Name: {full_name}\nEmail: {email}\nPhone: {phone}\n\n{body}",
                    from_email=None,
                    recipient_list=["support@marketnest.com"],
                    fail_silently=False,
                )
            except Exception:
                messages.error(request, "We could not submit your message. Please try again later.")
            else:
                messages.success(request, "Thank you. Your message has been submitted to MarketNest support.")
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
