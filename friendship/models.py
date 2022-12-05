from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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
    is_cleaned = False
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
    accepted = models.BooleanField(default=False)

    def clean(self):
        self.is_cleaned = True
        if self.rejected is True and self.accepted is True:
            raise ValidationError(
                "Both rejected and accepted cannot be True at the same time."
            )
        if self.to_user == self.from_user:
            raise ValidationError("You cannot friend yourself")
        super(FriendshipRequests, self).clean()

    def save(self, *args, **kwargs):
        if not self.is_cleaned:
            self.full_clean()
        super(FriendshipRequests, self).save(*args, **kwargs)

    class Meta:
        unique_together = ("from_user", "to_user")
