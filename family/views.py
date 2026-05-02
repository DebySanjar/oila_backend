from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Sum
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Task, Reward, RewardClaim, UserPoints, ChatMessage, ChatReadReceipt
from .serializers import (
    TaskSerializer, TaskUpdateSerializer,
    RewardSerializer, RewardClaimSerializer, RewardClaimUpdateSerializer,
    UserPointsSerializer, ChatMessageSerializer, ChatMessageCreateSerializer,
    ChatReadReceiptSerializer
)
from accounts.permissions import IsParent

User = get_user_model()


class TaskListCreateView(generics.ListCreateAPIView):
    """
    Tasks list and create
    
    Vazifalar ro'yxati va yaratish
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        status_filter = self.request.query_params.get('status')
        assigned_to = self.request.query_params.get('assigned_to')
        
        # Base query - family tasks only
        queryset = Task.objects.filter(family_code=user.family_code)
        
        # Children see only their tasks
        if user.user_type == 'child':
            queryset = queryset.filter(assigned_to=user)
        
        # Filter by status
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by assigned user (parents only)
        if assigned_to and user.user_type == 'parent':
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        return queryset
    
    @swagger_auto_schema(
        operation_description="Vazifalar ro'yxati",
        manual_parameters=[
            openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('assigned_to', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ],
        responses={200: TaskSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Yangi vazifa yaratish (faqat ota-onalar)",
        responses={201: TaskSerializer}
    )
    def post(self, request, *args, **kwargs):
        if request.user.user_type != 'parent':
            return Response(
                {'error': 'Faqat ota-onalar vazifa yaratishi mumkin'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().post(request, *args, **kwargs)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Task detail, update, delete
    
    Vazifa tafsilotlari
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(family_code=user.family_code)
        
        # Children can only see their tasks
        if user.user_type == 'child':
            queryset = queryset.filter(assigned_to=user)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return TaskUpdateSerializer
        return TaskSerializer
    
    @swagger_auto_schema(
        operation_description="Vazifa tafsilotlari",
        responses={200: TaskSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Vazifa holatini yangilash",
        request_body=TaskUpdateSerializer,
        responses={200: TaskSerializer}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        # Only parents can delete
        if request.user.user_type != 'parent':
            return Response(
                {'error': 'Faqat ota-onalar vazifani o\'chirishi mumkin'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)


class MyTasksView(APIView):
    """
    Get current user's tasks
    
    Mening vazifalarim
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Mening vazifalarim",
        responses={200: TaskSerializer(many=True)}
    )
    def get(self, request):
        tasks = Task.objects.filter(
            assigned_to=request.user,
            status__in=['pending', 'in_progress']
        )
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class RewardListCreateView(generics.ListCreateAPIView):
    """
    Rewards list and create
    
    Mukofotlar ro'yxati
    """
    serializer_class = RewardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Reward.objects.filter(
            family_code=user.family_code,
            is_active=True
        )
        return queryset
    
    @swagger_auto_schema(
        operation_description="Mukofotlar ro'yxati",
        responses={200: RewardSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Yangi mukofot yaratish (faqat ota-onalar)",
        responses={201: RewardSerializer}
    )
    def post(self, request, *args, **kwargs):
        if request.user.user_type != 'parent':
            return Response(
                {'error': 'Faqat ota-onalar mukofot yaratishi mumkin'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().post(request, *args, **kwargs)


class RewardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Reward detail, update, delete
    
    Mukofot tafsilotlari
    """
    serializer_class = RewardSerializer
    permission_classes = [permissions.IsAuthenticated, IsParent]
    
    def get_queryset(self):
        return Reward.objects.filter(
            family_code=self.request.user.family_code
        )


class RewardClaimListCreateView(generics.ListCreateAPIView):
    """
    Reward claims list and create
    
    Mukofot so'rovlari
    """
    serializer_class = RewardClaimSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Parents see all family claims
        if user.user_type == 'parent':
            return RewardClaim.objects.filter(
                user__family_code=user.family_code
            )
        
        # Children see only their claims
        return RewardClaim.objects.filter(user=user)
    
    @swagger_auto_schema(
        operation_description="Mukofot so'rovlari ro'yxati",
        responses={200: RewardClaimSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Mukofot so'rash",
        responses={201: RewardClaimSerializer}
    )
    def post(self, request, *args, **kwargs):
        # Check if user has enough points
        reward_id = request.data.get('reward')
        try:
            reward = Reward.objects.get(id=reward_id, family_code=request.user.family_code)
            user_points = UserPoints.objects.get(user=request.user)
            
            if user_points.available_points < reward.points_required:
                return Response(
                    {'error': 'Yetarli ball yo\'q'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (Reward.DoesNotExist, UserPoints.DoesNotExist):
            return Response(
                {'error': 'Mukofot yoki ball topilmadi'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return super().post(request, *args, **kwargs)


class RewardClaimDetailView(generics.RetrieveUpdateAPIView):
    """
    Reward claim detail and update
    
    Mukofot so'rovi tafsilotlari
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'parent':
            return RewardClaim.objects.filter(user__family_code=user.family_code)
        return RewardClaim.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return RewardClaimUpdateSerializer
        return RewardClaimSerializer
    
    @swagger_auto_schema(
        operation_description="Mukofot so'rovi tafsilotlari",
        responses={200: RewardClaimSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Mukofot so'rovini tasdiqlash/rad etish (faqat ota-onalar)",
        request_body=RewardClaimUpdateSerializer,
        responses={200: RewardClaimSerializer}
    )
    def patch(self, request, *args, **kwargs):
        if request.user.user_type != 'parent':
            return Response(
                {'error': 'Faqat ota-onalar tasdiqlashi mumkin'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().patch(request, *args, **kwargs)


class UserPointsView(APIView):
    """
    Get user points
    
    Foydalanuvchi ballari
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Foydalanuvchi ballari",
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ],
        responses={200: UserPointsSerializer}
    )
    def get(self, request):
        user = request.user
        user_id = request.query_params.get('user_id')
        
        # Parents can view family members' points
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
        
        # Get or create user points
        user_points, created = UserPoints.objects.get_or_create(user=target_user)
        serializer = UserPointsSerializer(user_points)
        return Response(serializer.data)


class FamilyPointsView(APIView):
    """
    Get all family members' points
    
    Oila a'zolarining ballari
    """
    permission_classes = [permissions.IsAuthenticated, IsParent]
    
    @swagger_auto_schema(
        operation_description="Oila a'zolarining ballari",
        responses={200: UserPointsSerializer(many=True)}
    )
    def get(self, request):
        family_members = User.objects.filter(family_code=request.user.family_code)
        points = []
        
        for member in family_members:
            user_points, created = UserPoints.objects.get_or_create(user=member)
            points.append(user_points)
        
        serializer = UserPointsSerializer(points, many=True)
        return Response(serializer.data)


class ChatMessageListCreateView(generics.ListCreateAPIView):
    """
    Chat messages list and create
    
    Oilaviy chat xabarlari
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        limit = int(self.request.query_params.get('limit', 50))
        
        return ChatMessage.objects.filter(
            family_code=user.family_code,
            is_deleted=False
        )[:limit]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ChatMessageCreateSerializer
        return ChatMessageSerializer
    
    @swagger_auto_schema(
        operation_description="Chat xabarlari ro'yxati",
        manual_parameters=[
            openapi.Parameter('limit', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, default=50),
        ],
        responses={200: ChatMessageSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Yangi xabar yuborish",
        request_body=ChatMessageCreateSerializer,
        responses={201: ChatMessageSerializer}
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # TODO: Send push notification to family members
        # TODO: Trigger WebSocket event for real-time chat
        
        return response


class ChatMessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Chat message detail, update, delete
    
    Chat xabari tafsilotlari
    """
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatMessage.objects.filter(
            family_code=self.request.user.family_code
        )
    
    def update(self, request, *args, **kwargs):
        message = self.get_object()
        
        # Only sender can edit
        if message.sender != request.user:
            return Response(
                {'error': 'Faqat yuboruvchi tahrirlashi mumkin'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.content = request.data.get('content', message.content)
        message.is_edited = True
        message.save()
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)
    
    def delete(self, request, *args, **kwargs):
        message = self.get_object()
        
        # Only sender can delete
        if message.sender != request.user:
            return Response(
                {'error': 'Faqat yuboruvchi o\'chirishi mumkin'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.is_deleted = True
        message.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class MarkMessageReadView(APIView):
    """
    Mark message as read
    
    Xabarni o'qilgan deb belgilash
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Xabarni o'qilgan deb belgilash",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={200: openapi.Response('Success')}
    )
    def post(self, request):
        message_id = request.data.get('message_id')
        
        try:
            message = ChatMessage.objects.get(
                id=message_id,
                family_code=request.user.family_code
            )
        except ChatMessage.DoesNotExist:
            return Response(
                {'error': 'Xabar topilmadi'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create read receipt
        receipt, created = ChatReadReceipt.objects.get_or_create(
            message=message,
            user=request.user
        )
        
        return Response({
            'message': 'Xabar o\'qilgan deb belgilandi',
            'created': created
        })
