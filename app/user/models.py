"""
User Model

"""


from django.db import models
from django.contrib.auth.models import(
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings
import os
import uuid


def image_file_path(instance, filename):
    """Generate filepath for new users"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'users', filename)


class UserManager(BaseUserManager):
    """Manager for Users"""

    def create_user(self, email, password=None, **extra_fields):
        """create, save and return new user"""
        if not email:
            raise ValueError('User must have an email address>')
        user = self.model(email = self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        "create and return superuser"
        user = self.create_user(email, password, **extra_fields)
        #user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)
        return user

    def create_staff(self, email, password, **extra_fields):
        """create and return staff user"""
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.save(using=self.db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=11)
    address = models.CharField(max_length=255)
    birth_day = models.DateField(null=True)
    status_choices = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ]
    gender = models.CharField(max_length=7, choices=status_choices, default='Male')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    image = models.ImageField(upload_to=image_file_path, blank=True, null=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'



