"""
Management command to create test users
Usage: python manage.py create_test_users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test users for development'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating test users...')
        
        # Create parent
        parent, created = User.objects.get_or_create(
            phone_number='+998901111111',
            defaults={
                'first_name': 'Test',
                'last_name': 'Parent',
                'user_type': 'parent',
                'date_of_birth': '1985-01-01'
            }
        )
        
        if created:
            parent.set_password('test123')
            parent.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Parent created: {parent.phone_number}'))
            self.stdout.write(self.style.SUCCESS(f'  Family Code: {parent.family_code}'))
        else:
            self.stdout.write(self.style.WARNING(f'Parent already exists: {parent.phone_number}'))
        
        # Create child
        child, created = User.objects.get_or_create(
            phone_number='+998902222222',
            defaults={
                'first_name': 'Test',
                'last_name': 'Child',
                'user_type': 'child',
                'family_code': parent.family_code,
                'date_of_birth': '2010-01-01'
            }
        )
        
        if created:
            child.set_password('test123')
            child.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Child created: {child.phone_number}'))
        else:
            self.stdout.write(self.style.WARNING(f'Child already exists: {child.phone_number}'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Test users created successfully!'))
        self.stdout.write('')
        self.stdout.write('Login credentials:')
        self.stdout.write(f'  Parent: {parent.phone_number} / test123')
        self.stdout.write(f'  Child:  {child.phone_number} / test123')
        self.stdout.write(f'  Family Code: {parent.family_code}')
