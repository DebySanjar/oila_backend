from django.urls import path
from .views import (
    SOSAlertCreateView,
    SOSAlertListView,
    SOSAlertDetailView,
    ActiveSOSAlertsView,
    SOSContactListCreateView,
    SOSContactDetailView
)

app_name = 'sos'

urlpatterns = [
    # SOS Alerts
    path('alert/', SOSAlertCreateView.as_view(), name='sos-create'),
    path('alerts/', SOSAlertListView.as_view(), name='sos-list'),
    path('alerts/<int:pk>/', SOSAlertDetailView.as_view(), name='sos-detail'),
    path('alerts/active/', ActiveSOSAlertsView.as_view(), name='sos-active'),
    
    # SOS Contacts
    path('contacts/', SOSContactListCreateView.as_view(), name='contact-list'),
    path('contacts/<int:pk>/', SOSContactDetailView.as_view(), name='contact-detail'),
]
