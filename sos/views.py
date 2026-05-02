from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import SOSAlert, SOSContact
from .serializers import (
    SOSAlertSerializer, SOSAlertCreateSerializer,
    SOSAlertUpdateSerializer, SOSContactSerializer
)
from accounts.permissions import IsParent

User = get_user_model()


class SOSAlertCreateView(generics.CreateAPIView):
    """
    Create SOS alert
    
    Favqulodda signal yuborish
    """
    serializer_class = SOSAlertCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="SOS signal yuborish",
        responses={201: SOSAlertSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        alert = serializer.save()
        
        # TODO: Send immediate notifications to all family members
        # TODO: Send SMS to emergency contacts
        # TODO: Trigger push notifications
        
        return Response(
            SOSAlertSerializer(alert).data,
            status=status.HTTP_201_CREATED
        )


class SOSAlertListView(generics.ListAPIView):
    """
    List SOS alerts
    
    SOS signallar ro'yxati
    """
    serializer_class = SOSAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        status_filter = self.request.query_params.get('status')
        
        # Get alerts from family members
        queryset = SOSAlert.objects.filter(
            user__family_code=user.family_code
        )
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @swagger_auto_schema(
        operation_description="SOS signallar ro'yxati",
        manual_parameters=[
            openapi.Parameter(
                'status', 
                openapi.IN_QUERY, 
                type=openapi.TYPE_STRING,
                enum=['active', 'acknowledged', 'resolved', 'false_alarm']
            )
        ],
        responses={200: SOSAlertSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SOSAlertDetailView(generics.RetrieveUpdateAPIView):
    """
    SOS alert detail and update
    
    SOS signal tafsilotlari va yangilash
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SOSAlert.objects.filter(
            user__family_code=self.request.user.family_code
        )
    
    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return SOSAlertUpdateSerializer
        return SOSAlertSerializer
    
    @swagger_auto_schema(
        operation_description="SOS signal tafsilotlari",
        responses={200: SOSAlertSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="SOS signal holatini yangilash (faqat ota-onalar)",
        request_body=SOSAlertUpdateSerializer,
        responses={200: SOSAlertSerializer}
    )
    def patch(self, request, *args, **kwargs):
        # Only parents can update
        if request.user.user_type != 'parent':
            return Response(
                {'error': 'Faqat ota-onalar yangilashi mumkin'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().patch(request, *args, **kwargs)


class ActiveSOSAlertsView(APIView):
    """
    Get active SOS alerts
    
    Faol SOS signallar
    """
    permission_classes = [permissions.IsAuthenticated, IsParent]
    
    @swagger_auto_schema(
        operation_description="Faol SOS signallar (faqat ota-onalar)",
        responses={200: SOSAlertSerializer(many=True)}
    )
    def get(self, request):
        alerts = SOSAlert.objects.filter(
            user__family_code=request.user.family_code,
            status='active'
        )
        serializer = SOSAlertSerializer(alerts, many=True)
        return Response(serializer.data)


class SOSContactListCreateView(generics.ListCreateAPIView):
    """
    SOS contacts list and create
    
    Favqulodda kontaktlar
    """
    serializer_class = SOSContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SOSContact.objects.filter(user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Favqulodda kontaktlar ro'yxati",
        responses={200: SOSContactSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Yangi favqulodda kontakt qo'shish",
        responses={201: SOSContactSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SOSContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    SOS contact detail, update, delete
    
    Favqulodda kontakt tafsilotlari
    """
    serializer_class = SOSContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SOSContact.objects.filter(user=self.request.user)
