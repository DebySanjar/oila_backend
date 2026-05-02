from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from datetime import timedelta, date
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import (
    ScreenTimeRule, AppUsage, BlockedApp,
    ContentFilter, BlockedContent, ScreenTimeSession
)
from .serializers import (
    ScreenTimeRuleSerializer, AppUsageSerializer, BlockedAppSerializer,
    ContentFilterSerializer, BlockedContentSerializer, ScreenTimeSessionSerializer,
    ScreenTimeStatsSerializer
)
from accounts.permissions import IsParent, IsSameFamily

User = get_user_model()


class ScreenTimeRuleListCreateView(generics.ListCreateAPIView):
    """
    Screen time rules list and create
    
    Ekran vaqti qoidalari
    """
    serializer_class = ScreenTimeRuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsParent]
    
    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return ScreenTimeRule.objects.filter(
                user_id=user_id,
                user__family_code=self.request.user.family_code
            )
        return ScreenTimeRule.objects.filter(
            created_by=self.request.user
        )
    
    @swagger_auto_schema(
        operation_description="Ekran vaqti qoidalari ro'yxati",
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
        ],
        responses={200: ScreenTimeRuleSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Yangi ekran vaqti qoidasi yaratish",
        responses={201: ScreenTimeRuleSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ScreenTimeRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Screen time rule detail, update, delete
    
    Ekran vaqti qoidasi tafsilotlari
    """
    serializer_class = ScreenTimeRuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsParent]
    
    def get_queryset(self):
        return ScreenTimeRule.objects.filter(
            created_by=self.request.user
        )


class AppUsageListCreateView(generics.ListCreateAPIView):
    """
    App usage list and create
    
    Ilova foydalanish statistikasi
    """
    serializer_class = AppUsageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        user_id = self.request.query_params.get('user_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        # Parents can view family members, children only themselves
        if user.user_type == 'parent' and user_id:
            queryset = AppUsage.objects.filter(
                user_id=user_id,
                user__family_code=user.family_code
            )
        else:
            queryset = AppUsage.objects.filter(user=user)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset
    
    @swagger_auto_schema(
        operation_description="Ilova foydalanish statistikasi",
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('start_date', openapi.IN_QUERY, type=openapi.TYPE_STRING, format='date'),
            openapi.Parameter('end_date', openapi.IN_QUERY, type=openapi.TYPE_STRING, format='date'),
        ],
        responses={200: AppUsageSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Ilova foydalanishni qayd qilish",
        responses={201: AppUsageSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class AppUsageStatsView(APIView):
    """
    App usage statistics
    
    Ilova foydalanish statistikasi (umumiy)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Ilova foydalanish statistikasi",
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('days', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, default=7),
        ],
        responses={200: openapi.Response('Statistics', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'total_duration_seconds': openapi.Schema(type=openapi.TYPE_INTEGER),
                'total_apps': openapi.Schema(type=openapi.TYPE_INTEGER),
                'most_used_apps': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                'daily_usage': openapi.Schema(type=openapi.TYPE_OBJECT),
            }
        ))}
    )
    def get(self, request):
        user = request.user
        user_id = request.query_params.get('user_id')
        days = int(request.query_params.get('days', 7))
        
        # Determine target user
        if user.user_type == 'parent' and user_id:
            try:
                target_user = User.objects.get(id=user_id, family_code=user.family_code)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Foydalanuvchi topilmadi'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            target_user = user
        
        # Get usage data
        start_date = date.today() - timedelta(days=days)
        usage = AppUsage.objects.filter(
            user=target_user,
            date__gte=start_date
        )
        
        # Calculate stats
        total_duration = usage.aggregate(Sum('duration_seconds'))['duration_seconds__sum'] or 0
        total_apps = usage.values('package_name').distinct().count()
        
        # Most used apps
        most_used = usage.values('app_name', 'package_name').annotate(
            total_time=Sum('duration_seconds')
        ).order_by('-total_time')[:10]
        
        # Daily breakdown
        daily_usage = {}
        for i in range(days):
            day = date.today() - timedelta(days=i)
            day_total = usage.filter(date=day).aggregate(
                Sum('duration_seconds')
            )['duration_seconds__sum'] or 0
            daily_usage[str(day)] = day_total
        
        return Response({
            'total_duration_seconds': total_duration,
            'total_duration_minutes': total_duration // 60,
            'total_duration_hours': round(total_duration / 3600, 2),
            'total_apps': total_apps,
            'most_used_apps': list(most_used),
            'daily_usage': daily_usage,
        })


class BlockedAppListCreateView(generics.ListCreateAPIView):
    """
    Blocked apps list and create
    
    Bloklangan ilovalar
    """
    serializer_class = BlockedAppSerializer
    permission_classes = [permissions.IsAuthenticated, IsParent]
    
    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return BlockedApp.objects.filter(
                user_id=user_id,
                user__family_code=self.request.user.family_code,
                is_active=True
            )
        return BlockedApp.objects.filter(
            blocked_by=self.request.user,
            is_active=True
        )
    
    @swagger_auto_schema(
        operation_description="Bloklangan ilovalar ro'yxati",
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
        ],
        responses={200: BlockedAppSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Ilovani bloklash",
        responses={201: BlockedAppSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class BlockedAppDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Blocked app detail, update, delete
    
    Bloklangan ilova tafsilotlari
    """
    serializer_class = BlockedAppSerializer
    permission_classes = [permissions.IsAuthenticated, IsParent]
    
    def get_queryset(self):
        return BlockedApp.objects.filter(
            blocked_by=self.request.user
        )


class ContentFilterListCreateView(generics.ListCreateAPIView):
    """
    Content filters list and create
    
    Kontent filtrlari
    """
    serializer_class = ContentFilterSerializer
    permission_classes = [permissions.IsAuthenticated, IsParent]
    
    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return ContentFilter.objects.filter(
                user_id=user_id,
                user__family_code=self.request.user.family_code,
                is_active=True
            )
        return ContentFilter.objects.filter(
            created_by=self.request.user,
            is_active=True
        )
    
    @swagger_auto_schema(
        operation_description="Kontent filtrlari ro'yxati",
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
        ],
        responses={200: ContentFilterSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Yangi kontent filtri yaratish",
        responses={201: ContentFilterSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ContentFilterDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Content filter detail, update, delete
    
    Kontent filtri tafsilotlari
    """
    serializer_class = ContentFilterSerializer
    permission_classes = [permissions.IsAuthenticated, IsParent]
    
    def get_queryset(self):
        return ContentFilter.objects.filter(
            created_by=self.request.user
        )


class BlockedContentListView(generics.ListAPIView):
    """
    Blocked content history
    
    Bloklangan kontent tarixi
    """
    serializer_class = BlockedContentSerializer
    permission_classes = [permissions.IsAuthenticated, IsParent]
    
    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        days = int(self.request.query_params.get('days', 7))
        
        start_date = timezone.now() - timedelta(days=days)
        
        if user_id:
            return BlockedContent.objects.filter(
                user_id=user_id,
                user__family_code=self.request.user.family_code,
                timestamp__gte=start_date
            )
        
        return BlockedContent.objects.filter(
            user__family_code=self.request.user.family_code,
            timestamp__gte=start_date
        )
    
    @swagger_auto_schema(
        operation_description="Bloklangan kontent tarixi",
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('days', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, default=7),
        ],
        responses={200: BlockedContentSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ScreenTimeSessionListCreateView(generics.ListCreateAPIView):
    """
    Screen time sessions list and create
    
    Ekran vaqti sessiyalari
    """
    serializer_class = ScreenTimeSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        user_id = self.request.query_params.get('user_id')
        days = int(self.request.query_params.get('days', 7))
        
        start_date = timezone.now() - timedelta(days=days)
        
        # Parents can view family members, children only themselves
        if user.user_type == 'parent' and user_id:
            queryset = ScreenTimeSession.objects.filter(
                user_id=user_id,
                user__family_code=user.family_code,
                start_time__gte=start_date
            )
        else:
            queryset = ScreenTimeSession.objects.filter(
                user=user,
                start_time__gte=start_date
            )
        
        return queryset
    
    @swagger_auto_schema(
        operation_description="Ekran vaqti sessiyalari",
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('days', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, default=7),
        ],
        responses={200: ScreenTimeSessionSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Yangi ekran vaqti sessiyasi boshlash",
        responses={201: ScreenTimeSessionSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ScreenTimeSessionDetailView(generics.RetrieveUpdateAPIView):
    """
    Screen time session detail and update
    
    Ekran vaqti sessiyasi tafsilotlari
    """
    serializer_class = ScreenTimeSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ScreenTimeSession.objects.filter(user=self.request.user)


class ScreenTimeStatsView(APIView):
    """
    Screen time statistics
    
    Ekran vaqti statistikasi
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Ekran vaqti statistikasi",
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('days', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, default=7),
        ],
        responses={200: ScreenTimeStatsSerializer}
    )
    def get(self, request):
        user = request.user
        user_id = request.query_params.get('user_id')
        days = int(request.query_params.get('days', 7))
        
        # Determine target user
        if user.user_type == 'parent' and user_id:
            try:
                target_user = User.objects.get(id=user_id, family_code=user.family_code)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Foydalanuvchi topilmadi'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            target_user = user
        
        # Get session data
        start_date = timezone.now() - timedelta(days=days)
        sessions = ScreenTimeSession.objects.filter(
            user=target_user,
            start_time__gte=start_date,
            end_time__isnull=False
        )
        
        # Calculate stats
        total_duration = sessions.aggregate(Sum('duration_seconds'))['duration_seconds__sum'] or 0
        session_count = sessions.count()
        avg_session = sessions.aggregate(Avg('duration_seconds'))['duration_seconds__avg'] or 0
        
        # Get app usage for most used apps
        app_usage = AppUsage.objects.filter(
            user=target_user,
            date__gte=(timezone.now() - timedelta(days=days)).date()
        ).values('app_name').annotate(
            total_time=Sum('duration_seconds')
        ).order_by('-total_time')[:5]
        
        # Daily breakdown
        daily_breakdown = {}
        for i in range(days):
            day = date.today() - timedelta(days=i)
            day_sessions = sessions.filter(start_time__date=day)
            day_total = day_sessions.aggregate(Sum('duration_seconds'))['duration_seconds__sum'] or 0
            daily_breakdown[str(day)] = {
                'duration_seconds': day_total,
                'duration_minutes': day_total // 60,
                'session_count': day_sessions.count()
            }
        
        return Response({
            'total_duration_seconds': total_duration,
            'total_duration_minutes': total_duration // 60,
            'total_duration_hours': round(total_duration / 3600, 2),
            'session_count': session_count,
            'average_session_minutes': round(avg_session / 60, 2),
            'most_used_apps': list(app_usage),
            'daily_breakdown': daily_breakdown,
        })
