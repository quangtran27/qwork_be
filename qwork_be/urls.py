from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="QWORK API",
        default_version='v1',),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
  path('', schema_view.with_ui('swagger', cache_timeout=0),name='schema-swagger-ui'),
  path('admin/', admin.site.urls),
  path('addresses/', include('addresses.urls')),
  path('applications/', include('applications.urls')),
  path('auth/', include('authentication.urls')),
  path('candidates/', include('candidates.urls')),
  path('recruiters/', include('recruiters.urls')),
  path('jobs/', include('jobs.urls')),
  path('users/', include('users.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)