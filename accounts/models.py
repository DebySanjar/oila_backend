from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import secrets
import string


def generate_family_code():
    """Generate unique 6-character family code"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))


class UserManager(BaseUserManager):
    """Custom user manager"""
    
    def create_user(self, phone_number, password=None, **extra_fields):
        """Create and save a regular user"""
        if not phone_number:
            raise ValueError('Phone number is required')
        
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'parent')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    """Custom User model"""
    USER_TYPE_CHOICES = (
        ('parent', 'Ota/Ona'),
        ('child', 'Farzand'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, unique=True)
    family_code = models.CharField(max_length=6, blank=True, null=True, db_index=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Remove username requirement
    username = models.CharField(max_length=150, blank=True, null=True)
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['user_type']
    
    # Use custom manager
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name() or self.phone_number} ({self.get_user_type_display()})"
    
    def save(self, *args, **kwargs):
        # Auto-generate family code for parents
        if self.user_type == 'parent' and not self.family_code:
            self.family_code = generate_family_code()
            # Ensure uniqueness
            while User.objects.filter(family_code=self.family_code).exists():
                self.family_code = generate_family_code()
        super().save(*args, **kwargs)


class Family(models.Model):
    """Family group model"""
    family_code = models.CharField(max_length=6, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_families')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'families'
        verbose_name = 'Family'
        verbose_name_plural = 'Families'
    
    def __str__(self):
        return f"{self.name} ({self.family_code})"
