"""
Utility functions for accounts app
"""
import secrets
import string
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_unique_family_code(length=6):
    """
    Generate a unique family code
    
    Args:
        length (int): Length of the code (default: 6)
    
    Returns:
        str: Unique family code
    """
    while True:
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))
        if not User.objects.filter(family_code=code).exists():
            return code


def validate_phone_number(phone):
    """
    Validate phone number format
    
    Args:
        phone (str): Phone number to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    # Remove spaces and special characters
    phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Check if starts with + and has 10-15 digits
    if phone.startswith('+') and len(phone) >= 11 and len(phone) <= 16:
        return phone[1:].isdigit()
    
    return False


def get_family_members(user):
    """
    Get all family members for a user
    
    Args:
        user (User): User object
    
    Returns:
        QuerySet: Family members
    """
    if not user.family_code:
        return User.objects.none()
    
    return User.objects.filter(family_code=user.family_code).exclude(id=user.id)


def is_parent(user):
    """
    Check if user is a parent
    
    Args:
        user (User): User object
    
    Returns:
        bool: True if parent, False otherwise
    """
    return user.user_type == 'parent'


def is_child(user):
    """
    Check if user is a child
    
    Args:
        user (User): User object
    
    Returns:
        bool: True if child, False otherwise
    """
    return user.user_type == 'child'
