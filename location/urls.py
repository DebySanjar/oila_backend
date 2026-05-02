from django.urls import path
from .views import (
    LocationUpdateView,
    CurrentLocationView,
    LocationHistoryView,
    SafeZoneListCreateView,
    SafeZoneDetailView,
    ZoneEventsView
)

app_name = 'location'

urlpatterns = [
    # Location tracking
    path('update/', LocationUpdateView.as_view(), name='location-update'),
    path('current/', CurrentLocationView.as_view(), name='current-location'),
    path('history/', LocationHistoryView.as_view(), name='location-history'),
    
    # Safe zones
    path('zones/', SafeZoneListCreateView.as_view(), name='zone-list'),
    path('zones/<int:pk>/', SafeZoneDetailView.as_view(), name='zone-detail'),
    path('zones/events/', ZoneEventsView.as_view(), name='zone-events'),
]
