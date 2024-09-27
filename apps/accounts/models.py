from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.core.validators import RegexValidator
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,14}$', 
        message="Phone number must be entered in the format +919999999999. Up to 14 digits allowed."
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(validators=[phone_regex], max_length=20, blank=True)
    api_key = models.UUIDField(default=uuid.uuid4, editable=False)
    secret = models.UUIDField( default=uuid.uuid4, editable=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()

    class Meta:
        verbose_name_plural = "Users"
    # def save(self, *args, **kwargs):
    #     # Auto-generate API key and secret only if they are not already set
    #     if not self.api_key:
    #         self.api_key = uuid.uuid4().hex  # Generate a unique API key
    #     if not self.secret:
    #         self.secret = secrets.token_hex(32)  # Generate a secure random secret (64 chars)
        
    #     super(User, self).save(*args, **kwargs)
