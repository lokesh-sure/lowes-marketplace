from django.db import OperationalError, ProgrammingError
from django.templatetags.static import static
from django.urls import reverse

from .models import StoreBranding


def store_branding(request):
    logo_url = static("images/preciouscart-logo.png")
    try:
        branding = StoreBranding.objects.filter(pk=1).only(
            "logo_content_type", "updated_at"
        ).first()
    except (OperationalError, ProgrammingError):
        # Keep pages usable during the short interval before migrations finish.
        branding = None
    if branding and branding.logo_content_type:
        version = int(branding.updated_at.timestamp())
        logo_url = f"{reverse('pages:brand_logo_image')}?v={version}"
    return {"store_logo_url": logo_url}
