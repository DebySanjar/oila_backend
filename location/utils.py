"""
Utility functions for location tracking
"""
import math
from .models import SafeZone, ZoneEvent


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points using Haversine formula
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
    
    Returns:
        float: Distance in meters
    """
    # Earth radius in meters
    R = 6371000
    
    # Convert to radians
    lat1_rad = math.radians(float(lat1))
    lat2_rad = math.radians(float(lat2))
    delta_lat = math.radians(float(lat2) - float(lat1))
    delta_lon = math.radians(float(lon2) - float(lon1))
    
    # Haversine formula
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def is_inside_zone(location, zone):
    """
    Check if location is inside safe zone
    
    Args:
        location: Location object
        zone: SafeZone object
    
    Returns:
        bool: True if inside zone
    """
    distance = calculate_distance(
        location.latitude, location.longitude,
        zone.latitude, zone.longitude
    )
    return distance <= zone.radius


def check_zone_entry(location):
    """
    Check if user entered or exited any safe zone
    
    Args:
        location: Location object
    
    Returns:
        list: List of created ZoneEvent objects
    """
    user = location.user
    
    # Get user's family safe zones
    zones = SafeZone.objects.filter(
        family_code=user.family_code,
        is_active=True
    )
    
    events = []
    
    for zone in zones:
        is_inside = is_inside_zone(location, zone)
        
        # Get last event for this zone
        last_event = ZoneEvent.objects.filter(
            user=user,
            zone=zone
        ).first()
        
        # Determine if we need to create an event
        should_create_event = False
        event_type = None
        
        if is_inside:
            # User is inside zone
            if not last_event or last_event.event_type == 'exit':
                # User just entered
                should_create_event = zone.notify_on_enter
                event_type = 'enter'
        else:
            # User is outside zone
            if last_event and last_event.event_type == 'enter':
                # User just exited
                should_create_event = zone.notify_on_exit
                event_type = 'exit'
        
        if should_create_event and event_type:
            event = ZoneEvent.objects.create(
                user=user,
                zone=zone,
                event_type=event_type,
                location=location
            )
            events.append(event)
    
    return events


def get_location_summary(user, days=7):
    """
    Get location summary for user
    
    Args:
        user: User object
        days: Number of days to analyze
    
    Returns:
        dict: Summary statistics
    """
    from django.utils import timezone
    from datetime import timedelta
    from .models import Location
    
    start_date = timezone.now() - timedelta(days=days)
    locations = Location.objects.filter(
        user=user,
        timestamp__gte=start_date
    )
    
    if not locations.exists():
        return {
            'total_locations': 0,
            'days_analyzed': days,
            'average_battery': None,
            'total_distance': 0
        }
    
    # Calculate statistics
    total_locations = locations.count()
    avg_battery = locations.aggregate(
        avg=models.Avg('battery_level')
    )['avg']
    
    # Calculate total distance traveled
    total_distance = 0
    prev_location = None
    
    for location in locations.order_by('timestamp'):
        if prev_location:
            distance = calculate_distance(
                prev_location.latitude, prev_location.longitude,
                location.latitude, location.longitude
            )
            total_distance += distance
        prev_location = location
    
    return {
        'total_locations': total_locations,
        'days_analyzed': days,
        'average_battery': round(avg_battery, 1) if avg_battery else None,
        'total_distance': round(total_distance, 2)
    }
