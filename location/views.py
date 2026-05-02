from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Location, SafeZone, ZoneEvent
from .serializers import (
    LocationSerializer, LocationCreateSerializer,
    SafeZoneSerializer, ZoneEventSerializer,
    LocationHistorySerializer
)
from .utils import calculate_distance, check_zone_entry
from accounts.permissions import IsParent, IsSameFamily

User = get_user_model()


class LocationUpdateView(generics.CreateAPIView):
    """
    Update current location
    
    Farzand o'z joylashuvini yangilaydi
    """
    serializer_class = LocationCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Joriy joylashuvni yangilash",
        responses={201: LocationSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        location = serializer.save()
        
        # Check safe zones
        check_zone_entry(location)
        
        return Response(
            LocationSerializer(location).data,
            status=status.HTTP_201_CREATED
        )


class CurrentLocationView(APIView):
    """
    Get current location of family members
    
    Oila a'zolarining joriy joylashuvini olish
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Oila a'zolarining joriy joylashuvi",
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="User ID (optional)")
        ],
        responses={200: LocationSerializer(many=True)}
    )
    def get(self, request):
        user = request.user
        user_id = request.query_params.get('user_id')
        
        # Get family members
        if user_id:
            # Specific user
            try:
                target_user = User.objects.get(id=user_id, family_code=user.family_code)
                users = [target_user]
            except User.DoesNotExist:
                return Response(
                    {'error': 'Foydalanuvchi topilmadi yoki bir oilada emas'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # All family members
            users = User.objects.filter(family_code=user.family_code).exclude(id=user.id)
        
        # Get latest location for each user
        locations = []
        for u in users:
            latest = Location.objects.filter(user=u).first()
            if latest:
                locations.append(latest)
        
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)


class LocationHistoryView(APIView):
    """
    Get location history
    
    Joylashuv tarixi
    """
    permission_classes = [permissions.IsAuthenticated, IsParent]
    
    @swagger_auto_schema(
        operation_description="Joylashuv tarixi (faqat ota-onalar)",
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('start_date', openapi.IN_QUERY, type=openapi.TYPE_STRING, format='date-time'),
            openapi.Parameter('end_date', openapi.IN_QUERY, type=openapi.TYPE_STRING, format='date-time'),
            openapi.Parameter('limit', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, default=100),
        ],
        responses={200: LocationSerializer(many=True)}
    )
    def get(self, request):
        user_id = request.query_params.get('user_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        limit = int(request.query_params.get('limit', 100))
        
        if not user_id:
            return Response(
                {'error': 'user_id majburiy'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is in same family
        try:
            target_user = User.objects.get(id=user_id, family_code=request.user.family_code)
        except User.DoesNotExist:
            return Response(
                {'error': 'Foydalanuvchi topilmadi'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Build query
        queryset = Location.objects.filter(user=target_user)
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        locations = queryset[:limit]
        serializer = LocationSerializer(locations, many=True)
        
        return Response(serializer.data)


class SafeZoneListCreateView(generics.ListCreateAPIView):
    """
    Safe zones list and create
    
    Xavfsiz hududlar ro'yxati va yaratish
    """
    serializer_class = SafeZoneSerializer
    permission_classes = [permissions.IsAuthenticated, IsParent]
    
    def get_queryset(self):
        return SafeZone.objects.filter(family_code=self.request.user.family_code)
    
    @swagger_auto_schema(
        operation_description="Xavfsiz hududlar ro'yxati",
        responses={200: SafeZoneSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Yangi xavfsiz hudud yaratish",
        responses={201: SafeZoneSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SafeZoneDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Safe zone detail, update, delete
    
    Xavfsiz hudud tafsilotlari
    """
    serializer_class = SafeZoneSerializer
    permission_classes = [permissions.IsAuthenticated, IsParent]
    
    def get_queryset(self):
        return SafeZone.objects.filter(family_code=self.request.user.family_code)


class ZoneEventsView(generics.ListAPIView):
    """
    Zone events history
    
    Hudud hodisalari tarixi
    """
    serializer_class = ZoneEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        zone_id = self.request.query_params.get('zone_id')
        user_id = self.request.query_params.get('user_id')
        days = int(self.request.query_params.get('days', 7))
        
        # Base query - family members only
        queryset = ZoneEvent.objects.filter(
            user__family_code=user.family_code,
            timestamp__gte=timezone.now() - timedelta(days=days)
        )
        
        if zone_id:
            queryset = queryset.filter(zone_id=zone_id)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset
    
    @swagger_auto_schema(
        operation_description="Hudud hodisalari tarixi",
        manual_parameters=[
            openapi.Parameter('zone_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('days', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, default=7),
        ],
        responses={200: ZoneEventSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
