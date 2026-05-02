"""
Custom validators for accounts app
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


def validate_phone_number(value):
    """
    Validate phone number format
    Must start with + and contain 10-15 digits
    """
    pattern = r'^\+\d{10,15}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Telefon raqam noto\'g\'ri formatda. Format: +998901234567'),
            code='invalid_phone'
        )


def validate_family_code(value):
    """
    Validate family code format
    Must be 6 characters, uppercase letters and digits only
    """
    pattern = r'^[A-Z0-9]{6}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Oila kodi 6 ta harf va raqamdan iborat bo\'lishi kerak'),
            code='invalid_family_code'
        )


def validate_age(value):
    """
    Validate age - must be between 1 and 120 years
    """
    from datetime import date
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    
    if age < 1 or age > 120:
        raise ValidationError(
            _('Yosh 1 dan 120 gacha bo\'lishi kerak'),
            code='invalid_age'
        )


def validate_password_strength(value):
    """
    Validate password strength
    Must be at least 6 characters
    """
    if len(value) < 6:
        raise ValidationError(
            _('Parol kamida 6 ta belgidan iborat bo\'lishi kerak'),
            code='password_too_short'
        )
    
    # Optional: Add more password rules
    # if not re.search(r'[A-Z]', value):
    #     raise ValidationError(_('Parolda kamida bitta katta harf bo\'lishi kerak'))
    
    # if not re.search(r'[0-9]', value):
    #     raise ValidationError(_('Parolda kamida bitta raqam bo\'lishi kerak'))
