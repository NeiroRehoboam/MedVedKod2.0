from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    use_in_migrations = True
    def create_user(self, max_id, password=None, **extra_fields):
        if not max_id: raise ValueError('max_id обязателен')
        user = self.model(max_id=max_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, max_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(max_id, password, **extra_fields)

class User(AbstractUser):
    username = None
    max_id = models.CharField(max_length=64, unique=True, verbose_name="ID в MAX")
    personal_salt = models.BinaryField(max_length=16, null=True, blank=True, editable=False)
    personal_key_encrypted = models.BinaryField(null=True, blank=True, editable=False)
    personal_key_version = models.PositiveIntegerField(default=1, editable=False)
    USERNAME_FIELD = "max_id"
    REQUIRED_FIELDS = []
    objects = UserManager()

    @property
    def has_personal_key(self):
        return bool(self.personal_salt and self.personal_key_encrypted)

    def __str__(self): return self.max_id
