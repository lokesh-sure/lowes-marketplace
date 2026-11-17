from django.db import models


class SalePoster(models.Model):
    """A homepage poster stored in the database so it survives Render deploys."""

    image_data = models.BinaryField()
    image_content_type = models.CharField(max_length=32)
    alt_text = models.CharField(max_length=200, default="Store sale poster")
    position = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("position", "id")

    def __str__(self):
        return f"Sale poster {self.position + 1}"


class StoreBranding(models.Model):
    """Admin-managed store logo, kept in the database across deployments."""

    logo_data = models.BinaryField(blank=True, null=True)
    logo_content_type = models.CharField(max_length=32, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "Store branding"
