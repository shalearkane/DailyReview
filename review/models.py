from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


# Create your models here.
class Review(models.Model):
    EVERYONE = "EV"
    ONLYME = "ME"
    FRIENDS = "FR"
    VISIBILITY_CHOICES = [
        (EVERYONE, "Everyone"),
        (ONLYME, "Only Me"),
        (FRIENDS, "Friends"),
    ]

    user = models.ForeignKey(
        User, null=False, blank=False, on_delete=models.CASCADE, editable=False
    )
    date = models.DateField(auto_now_add=True, editable=False)
    visibility = models.CharField(
        choices=VISIBILITY_CHOICES,
        max_length=2,
        default=EVERYONE,
        blank=False,
        null=False,
    )

    title = models.CharField(max_length=255, default="Today's Review")
    text = models.TextField()
    personal_thoughts = models.TextField(blank=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            "user",
            "date",
        )

    def get_absolute_url(self):
        return reverse("review-details", kwargs={"pk": self.pk})
