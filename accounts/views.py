from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from family.models import Family

from .serializers import (
    ParentRegisterSerializer,
    ChildRegisterSerializer,
    LoginSerializer,
    UserSerializer,
    CreateFamilySerializer,
    JoinFamilySerializer,
)

User = get_user_model()


class CreateFamilyView(generics.CreateAPIView):
    """
    Yangi oila yaratish (Kattalar uchun)
    
    Ota, Ona, Bobo yoki Buvi yangi oila yaratadi va oila kodi oladi.
    """
    serializer_class = CreateFamilySerializer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Yangi oila yaratish. Faqat kattalar (father, mother, grandfather, grandmother) yarata oladi.",
        responses={
            201: openapi.Response(
                description="Muvaffaqiyatli oila yaratildi",
                examples={
                    "application/json": {
                        "message": "Oila muvaffaqiyatli yaratildi",
                        "user": {},
                        "family": {
                            "family_code": "ABC123",
                            "family_name": "Dasturchilar oilasi"
                        }
                    }
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, family = serializer.save()
        
        return Response({
            'message': 'Oila muvaffaqiyatli yaratildi',
            'user': UserSerializer(user).data,
            'family': {
                'family_code': family.family_code,
                'family_name': family.family_name,
            }
        }, status=status.HTTP_201_CREATED)


class JoinFamilyView(generics.CreateAPIView):
    """
    Mavjud oilaga qo'shilish
    
    Kattalar va bolalar oila kodi orqali oilaga qo'shiladi.
    """
    serializer_class = JoinFamilySerializer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Mavjud oilaga qo'shilish. Oila kodi talab qilinadi.",
        responses={
            201: openapi.Response(
                description="Muvaffaqiyatli oilaga qo'shildi",
                schema=UserSerializer
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Get family info
        family = Family.objects.get(family_code=user.family_code)
        
        return Response({
            'message': 'Muvaffaqiyatli oilaga qo\'shildingiz',
            'user': UserSerializer(user).data,
            'family': {
                'family_code': family.family_code,
                'family_name': family.family_name,
            }
        }, status=status.HTTP_201_CREATED)


class ParentRegisterView(generics.CreateAPIView):
    """
    Ota/Ona royxatdan otish (DEPRECATED)
    
    Eski API - CreateFamilyView yoki JoinFamilyView ishlatish tavsiya etiladi.
    """
    serializer_class = ParentRegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Ota/Ona royxatdan otish. Avtomatik oila kodi beriladi. (DEPRECATED)",
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


class FamilyInfoView(APIView):
    """
    Oila ma'lumotlari - family_name va a'zolar soni
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.family_code:
            return Response(
                {'detail': 'Siz hech qanday oilaga tegishli emassiz.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            family = Family.objects.get(family_code=user.family_code)
            members = User.objects.filter(family_code=user.family_code)
            return Response({
                'family_code': family.family_code,
                'family_name': family.family_name,
                'members_count': members.count(),
                'members': UserSerializer(members, many=True).data,
            })
        except Family.DoesNotExist:
            return Response(
                {'detail': 'Oila topilmadi.'},
                status=status.HTTP_404_NOT_FOUND,
            )
