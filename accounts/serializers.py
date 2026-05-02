from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'user_type', 
                  'family_code', 'avatar', 'date_of_birth', 'created_at']
        read_only_fields = ['id', 'created_at']


class ParentRegisterSerializer(serializers.ModelSerializer):
    """Parent registration serializer"""
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
    """Child registration serializer"""
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
