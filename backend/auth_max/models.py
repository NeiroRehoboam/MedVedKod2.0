from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
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
    
    groups = models.ManyToManyField(Group, verbose_name='groups', blank=True,
        help_text='The groups this user belongs to.', related_name="auth_max_user_groups", related_query_name="auth_max_user")
    user_permissions = models.ManyToManyField(Permission, verbose_name='user permissions', blank=True,
        help_text='Specific permissions for this user.', related_name="auth_max_user_permissions", related_query_name="auth_max_user")

    USERNAME_FIELD = "max_id"
    REQUIRED_FIELDS = []
    objects = UserManager()
    def __str__(self): return self.max_id