from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    ParentRegisterSerializer,
    ChildRegisterSerializer,
    LoginSerializer,
    UserSerializer
)

User = get_user_model()


class ParentRegisterView(generics.CreateAPIView):
    """
    Ota/Ona royxatdan otish
    
    Ota yoki ona royxatdan otganda avtomatik oila kodi generatsiya qilinadi.
    """
    serializer_class = ParentRegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Ota/Ona royxatdan otish. Avtomatik oila kodi beriladi.",
        responses={
            201: openapi.Response(
                description="Muvaffaqiyatli royxatdan otildi",
                schema=UserSerializer
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'Muvaffaqiyatli royxatdan otildi',
            'user': UserSerializer(user).data,
            'family_code': user.family_code
        }, status=status.HTTP_201_CREATED)


class ChildRegisterView(generics.CreateAPIView):
    """
    Farzand royxatdan otish
    
    Farzand ota-onaning oila kodi orqali royxatdan otadi.
    """
    serializer_class = ChildRegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Farzand royxatdan otish. Oila kodi talab qilinadi.",
        responses={
            201: openapi.Response(
                description="Muvaffaqiyatli royxatdan otildi",
                schema=UserSerializer
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'Muvaffaqiyatli royxatdan otildi',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    Login - Kirish
    
    Telefon raqam va parol orqali tizimga kirish.
    """
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Tizimga kirish",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Muvaffaqiyatli kirildi",
                examples={
                    "application/json": {
                        "user": {},
                        "tokens": {
                            "refresh": "token",
                            "access": "token"
                        }
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Foydalanuvchi profili
    
    Foydalanuvchi oz profilini korish va tahrirlash.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class FamilyMembersView(generics.ListAPIView):
    """
    Oila azolari royxati
    
    Bir oilaga tegishli barcha foydalanuvchilar.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.family_code:
            return User.objects.filter(family_code=user.family_code).exclude(id=user.id)
        return User.objects.none()
