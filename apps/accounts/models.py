from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import uuid

class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model where email is the unique identifier
    for authentication instead of usernames.
    """
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    USER_TYPE_CHOICES = (
        (1, 'Student'),
        (2, 'Event Organizer'),
    )
    
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=1)
    is_verified = models.BooleanField(default=False)
    verification_uuid = models.UUIDField(default=uuid.uuid4, editable=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    groups = models.ManyToManyField(
        Group,
        related_name='accounts_user_set',  # Unique related_name
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='accounts_user_permissions_set',  # Unique related_name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


class Profile(models.Model):
    """Extended user profile information"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Student-specific fields
    institution = models.CharField(max_length=100, blank=True)
    course_of_study = models.CharField(max_length=100, blank=True)
    
    # Organizer-specific fields
    organization = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    def __str__(self):
        return f"{self.user.email}'s Profile"

    @property
    def age(self):
        if self.birth_date:
            return timezone.now().year - self.birth_date.year
        return None


class PasswordResetToken(models.Model):
    """Model for storing password reset tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('password reset token')
        verbose_name_plural = _('password reset tokens')

    def is_valid(self):
        """Check if the token is still valid"""
        return not self.is_used and timezone.now() < self.expires_at

    def mark_as_used(self):
        """Mark token as used"""
        self.is_used = True
        self.save()


class EmailVerificationToken(models.Model):
    """Model for storing email verification tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('email verification token')
        verbose_name_plural = _('email verification tokens')

    def is_valid(self):
        """Check if the token is still valid"""
        return not self.is_used and timezone.now() < self.expires_at

    def mark_as_used(self):
        """Mark token as used"""
        self.is_used = True
        self.save()


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email