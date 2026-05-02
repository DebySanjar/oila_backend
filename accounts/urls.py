from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    ParentRegisterView,
    ChildRegisterView,
    LoginView,
    UserProfileView,
    FamilyMembersView
)

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/parent/', ParentRegisterView.as_view(), name='parent-register'),
    path('register/child/', ChildRegisterView.as_view(), name='child-register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('family/members/', FamilyMembersView.as_view(), name='family-members'),
]
