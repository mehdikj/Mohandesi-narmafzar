from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Super Admin"
        LIBRARIAN = "LIBRARIAN", "Librarian / Archivist"
        USER = "USER", "Registered User"
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    display_name = models.CharField(max_length=150, blank=True)
    objects = UserManager()
    def is_librarian(self):
        return self.role in (self.Role.ADMIN, self.Role.LIBRARIAN) or self.is_superuser
    def is_super_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser
