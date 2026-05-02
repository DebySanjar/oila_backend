from django.urls import path
from .views import (
    TaskListCreateView,
    TaskDetailView,
    MyTasksView,
    RewardListCreateView,
    RewardDetailView,
    RewardClaimListCreateView,
    RewardClaimDetailView,
    UserPointsView,
    FamilyPointsView,
    ChatMessageListCreateView,
    ChatMessageDetailView,
    MarkMessageReadView,
)

app_name = 'family'

urlpatterns = [
    # Tasks
    path('tasks/', TaskListCreateView.as_view(), name='task-list'),
    path('tasks/my/', MyTasksView.as_view(), name='my-tasks'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    
    # Rewards
    path('rewards/', RewardListCreateView.as_view(), name='reward-list'),
    path('rewards/<int:pk>/', RewardDetailView.as_view(), name='reward-detail'),
    
    # Reward claims
    path('reward-claims/', RewardClaimListCreateView.as_view(), name='reward-claim-list'),
    path('reward-claims/<int:pk>/', RewardClaimDetailView.as_view(), name='reward-claim-detail'),
    
    # Points
    path('points/', UserPointsView.as_view(), name='user-points'),
    path('points/family/', FamilyPointsView.as_view(), name='family-points'),
    
    # Chat
    path('chat/', ChatMessageListCreateView.as_view(), name='chat-list'),
    path('chat/<int:pk>/', ChatMessageDetailView.as_view(), name='chat-detail'),
    path('chat/mark-read/', MarkMessageReadView.as_view(), name='mark-read'),
]
