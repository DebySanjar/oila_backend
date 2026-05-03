from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from family.models import Family

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    # Override avatar field to accept both file and URL
    avatar = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'user_type', 
                  'family_code', 'avatar', 'date_of_birth', 'created_at']
        read_only_fields = ['id', 'created_at']


class CreateFamilySerializer(serializers.Serializer):
    """Create new family serializer"""
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    user_type = serializers.ChoiceField(choices=['father', 'mother', 'grandfather', 'grandmother'])
    family_name = serializers.CharField(max_length=200, help_text="Oila nomi")
    date_of_birth = serializers.DateField(required=False)
    
    def validate_user_type(self, value):
        """Validate user type is parent"""
        if value not in ['father', 'mother', 'grandfather', 'grandmother']:
            raise serializers.ValidationError("Faqat kattalar oila yarata oladi")
        return value
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Parollar mos kelmadi"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        family_name = validated_data.pop('family_name')
        
        # Generate unique family code
        family_code = Family.generate_family_code()
        
        # Create family
        family = Family.objects.create(
            family_code=family_code,
            family_name=family_name
        )
        
        # Create user
        user = User.objects.create(
            **validated_data,
            family_code=family_code
        )
        user.set_password(password)
        user.save()
        
        # Set family creator
        family.created_by = user
        family.save()
        
        return user, family


class JoinFamilySerializer(serializers.Serializer):
    """Join existing family serializer"""
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    user_type = serializers.ChoiceField(
        choices=['father', 'mother', 'grandfather', 'grandmother', 'son', 'daughter']
    )
    family_code = serializers.CharField(max_length=6)
    date_of_birth = serializers.DateField(required=False)
    
    def validate_family_code(self, value):
        """Validate family code exists"""
        if not Family.objects.filter(family_code=value).exists():
            raise serializers.ValidationError("Oila kodi topilmadi")
        return value.upper()
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Parollar mos kelmadi"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        return user


class ParentRegisterSerializer(serializers.ModelSerializer):
    """Parent registration serializer (DEPRECATED - use CreateFamily or JoinFamily)"""
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['phone_number', 'first_name', 'last_name', 'password', 
                  'password_confirm', 'date_of_birth']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Parollar mos kelmadi"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create(
            **validated_data,
            user_type='parent'
        )
        user.set_password(password)
        user.save()
        
        return user


class ChildRegisterSerializer(serializers.ModelSerializer):
    """Child registration serializer (DEPRECATED - use JoinFamily)"""
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    family_code = serializers.CharField(required=True, max_length=6)
    
    class Meta:
        model = User
        fields = ['phone_number', 'first_name', 'last_name', 'password', 
                  'password_confirm', 'family_code', 'date_of_birth']
    
    def validate_family_code(self, value):
        if not User.objects.filter(family_code=value, user_type='parent').exists():
            raise serializers.ValidationError("Oila kodi topilmadi")
        return value
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Parollar mos kelmadi"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create(
            **validated_data,
            user_type='child'
        )
        user.set_password(password)
        user.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    """Login serializer"""
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')
        
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError("Telefon raqam yoki parol noto'g'ri")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Telefon raqam yoki parol noto'g'ri")
        
        if not user.is_active:
            raise serializers.ValidationError("Foydalanuvchi faol emas")
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return {
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }
