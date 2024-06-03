from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    username = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class OAuthAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    oauth_name = models.CharField(max_length=100, db_index=True)
    access_token = models.CharField(max_length=1024)
    expires_at = models.IntegerField(null=True)
    refresh_token = models.CharField(max_length=1024, blank=True, null=True)
    account_id = models.CharField(max_length=320, db_index=True, unique=True)
    account_email = models.CharField(max_length=320, blank=True, null=True)

    class Meta:
        unique_together = ("oauth_name", "user")
        verbose_name = "OAuth Account"
        verbose_name_plural = "OAuth Accounts"

    def update_account(
        self, access_token: str, expires_at: int, refresh_token: str
    ) -> None:
        self.access_token = access_token
        self.expires_at = expires_at
        self.refresh_token = refresh_token
        self.save(
            update_fields=("access_token", "expires_at", "refresh_token")
        )
