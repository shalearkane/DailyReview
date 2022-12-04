from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Friendship(models.Model):
    # you
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="fs_from",
        editable=False,
    )
    # your friend
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="fs_to",
        editable=False,
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("from_user", "to_user")


class FriendshipRequests(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="fr_from",
        editable=False,
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="fr_to",
        editable=False,
    )

    created = models.DateTimeField(auto_now_add=True, editable=False)
    rejected = models.BooleanField(default=False)

    class Meta:
        unique_together = ("from_user", "to_user")
