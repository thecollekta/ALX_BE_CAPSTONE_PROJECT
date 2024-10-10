# library_management_system/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from django.conf.urls.static import static

# Importing router from the accounts, books and transaction apps
from accounts.urls import router as accounts_router
from books.urls import router as books_router
from transactions.urls import router as transactions_router

# API documentation schema setup
schema_view = get_schema_view(
   openapi.Info(
      title="Library Management System API",
      default_version='v1',
      description="Library Management API Documentation",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="support@lms.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   authentication_classes=[JWTAuthentication],
   permission_classes=(permissions.AllowAny,),
)

# Main API router
router = DefaultRouter()

# Includes URLs from the accounts, books and transaction routers
router.registry.extend(accounts_router.registry)
router.registry.extend(books_router.registry)
router.registry.extend(transactions_router.registry)

urlpatterns = [
   path('', include(router.urls)),  # Includes all the registered routes
   path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
   path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
   path('docs/', include_docs_urls(title='Library Management System API')),  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)