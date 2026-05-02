from django.urls import path
from .views import (
    ScreenTimeRuleListCreateView,
    ScreenTimeRuleDetailView,
    AppUsageListCreateView,
    AppUsageStatsView,
    BlockedAppListCreateView,
    BlockedAppDetailView,
    ContentFilterListCreateView,
    ContentFilterDetailView,
    BlockedContentListView,
    ScreenTimeSessionListCreateView,
    ScreenTimeSessionDetailView,
    ScreenTimeStatsView,
)

app_name = 'monitoring'

urlpatterns = [
    # Screen time rules
    path('screen-time/rules/', ScreenTimeRuleListCreateView.as_view(), name='screen-time-rules'),
    path('screen-time/rules/<int:pk>/', ScreenTimeRuleDetailView.as_view(), name='screen-time-rule-detail'),
    
    # Screen time sessions
    path('screen-time/sessions/', ScreenTimeSessionListCreateView.as_view(), name='screen-time-sessions'),
    path('screen-time/sessions/<int:pk>/', ScreenTimeSessionDetailView.as_view(), name='screen-time-session-detail'),
    path('screen-time/stats/', ScreenTimeStatsView.as_view(), name='screen-time-stats'),
    
    # App usage
    path('app-usage/', AppUsageListCreateView.as_view(), name='app-usage'),
    path('app-usage/stats/', AppUsageStatsView.as_view(), name='app-usage-stats'),
    
    # Blocked apps
    path('blocked-apps/', BlockedAppListCreateView.as_view(), name='blocked-apps'),
    path('blocked-apps/<int:pk>/', BlockedAppDetailView.as_view(), name='blocked-app-detail'),
    
    # Content filters
    path('content-filters/', ContentFilterListCreateView.as_view(), name='content-filters'),
    path('content-filters/<int:pk>/', ContentFilterDetailView.as_view(), name='content-filter-detail'),
    path('blocked-content/', BlockedContentListView.as_view(), name='blocked-content'),
]
