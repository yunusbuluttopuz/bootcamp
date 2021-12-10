from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.db import models

from customers.managers import CustomerManager
from core.models import BaseAbstractModel
from phonenumber_field.modelfields import PhoneNumberField



class Country(BaseAbstractModel):
    name = models.CharField(max_length=20, verbose_name=_("name"), blank=True)

    class Meta:
        verbose_name = _("city")
        verbose_name_plural = _("cities")

    def __str__(self):
        return f"{self.name}"

class City(BaseAbstractModel):
    name = models.CharField(max_length=20, verbose_name=_("name"), blank=True)
    country = models.ForeignKey(Country,verbose_name=_("country"),on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = _("city")
        verbose_name_plural = _("cities")

    def __str__(self):
        return f"{self.name}"


class Address(BaseAbstractModel):
    name = models.CharField(max_length=50, verbose_name=_("name"), blank=True)
    full_name = models.CharField(max_length=200, verbose_name=_("full name"), blank=True)
    line1 = models.TextField(max_length=200,verbose_name=_("line 1"), blank=False)
    line2 = models.TextField(max_length=200,verbose_name=_("line 2"), blank=True)
    phone = PhoneNumberField()
    district = models.CharField(max_length=50,verbose_name=_("district"))
    postcode = models.PositiveBigIntegerField(verbose_name=_("postcode"))
    city = models.ForeignKey(City,verbose_name=_("city") ,on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = _("address")
        verbose_name_plural = _("adresses")

    def __str__(self):
        return f"{self.name}"

class Customer(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """

    username_validator = UnicodeUsernameValidator()

    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(
        _("email address"), unique=True, validators=[username_validator]
    )
    address = models.OneToOneField(Address,on_delete=models.CASCADE,)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = CustomerManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("customer")
        verbose_name_plural = _("customers")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)