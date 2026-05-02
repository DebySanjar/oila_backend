"""
URL configuration for oila_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Oila Safety API",
        default_version='v1',
        description="""
        # Oila Safety Backend API
        
        Bu API oila xavfsizligi va nazorat tizimi uchun backend.
        
        ## Asosiy funksiyalar:
        - 📍 Real-time joylashuv kuzatuvi
        - 🔒 Xavfsiz hududlar boshqaruvi
        - 🚨 SOS signal tizimi
        - ⏰ Vaqt va kontent nazorati
        - 👨‍👩‍👧‍👦 Oilaviy aloqa va vazifalar
        
        ## Autentifikatsiya:
        API JWT (JSON Web Token) autentifikatsiyasidan foydalanadi.
        
        1. `/api/accounts/login/` orqali login qiling
        2. Olingan `access` tokenni `Authorization: Bearer <token>` header sifatida yuboring
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@oilasafety.uz"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API
    path('api/accounts/', include('accounts.urls')),
    path('api/location/', include('location.urls')),
    path('api/sos/', include('sos.urls')),
    path('api/monitoring/', include('monitoring.urls')),
    path('api/family/', include('family.urls')),
    
    # Swagger Documentation
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

# Media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
