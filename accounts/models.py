import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import secrets
from django.utils import timezone

from accounts.managers import UserManager

class User(AbstractUser):
    username = None  # On utilise email comme identifiant principal
    email = models.EmailField(_('email address'), unique=True)
    public_key = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)  # Désactivé jusqu’à activation
    is_staff = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users'
    )
    must_change_password = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    


class InvitationToken(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    token = models.CharField(max_length=128, unique=True, default=secrets.token_urlsafe)
    invited_email = models.EmailField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at

    def __str__(self):
        return f"Invitation for {self.invited_email}"