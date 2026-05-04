from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    ParentRegisterView,
    ChildRegisterView,
    LoginView,
    UserProfileView,
    FamilyMembersView,
    FamilyInfoView,
    CreateFamilyView,
    JoinFamilyView,
)

app_name = 'accounts'

urlpatterns = [
    # New Registration (Recommended)
    path('family/create/', CreateFamilyView.as_view(), name='create-family'),
    path('family/join/', JoinFamilyView.as_view(), name='join-family'),
    
    # Old Registration (Deprecated but kept for compatibility)
    path('register/parent/', ParentRegisterView.as_view(), name='parent-register'),
    path('register/child/', ChildRegisterView.as_view(), name='child-register'),
    
    # Authentication
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('family/members/', FamilyMembersView.as_view(), name='family-members'),
    path('family/info/', FamilyInfoView.as_view(), name='family-info'),
]
