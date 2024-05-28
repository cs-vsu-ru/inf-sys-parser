from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = []

urlpatterns += [
    path('api/__docs__/', SpectacularAPIView.as_view(), name='__docs__'),
    path('api/', SpectacularSwaggerView.as_view(url_name='__docs__')),
    path('api/lessons/', include('app.lessons.urls')),
    path('api/employees/', include('app.employees.urls')),
    *static(settings.BASE_STATIC_URL, document_root=settings.STATIC_ROOT),
]
