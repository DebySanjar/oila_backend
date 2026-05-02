#!/usr/bin/env python
"""
Superuser yaratish uchun script
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oila_backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Superuser yaratish
phone = '+998934941522'
password = '12345678'

if User.objects.filter(phone_number=phone).exists():
    print(f"❌ {phone} raqamli foydalanuvchi allaqachon mavjud!")
    user = User.objects.get(phone_number=phone)
    print(f"✅ Mavjud foydalanuvchi: {user}")
else:
    user = User.objects.create_superuser(
        phone_number=phone,
        password=password,
        first_name='Admin',
        last_name='User',
        user_type='parent'
    )
    print(f"✅ Superuser yaratildi!")
    print(f"📱 Phone: {phone}")
    print(f"🔑 Password: {password}")
    print(f"👤 User type: parent")
    print(f"🏠 Family code: {user.family_code}")
    print(f"\n🌐 Admin panel: http://127.0.0.1:8000/admin/")
