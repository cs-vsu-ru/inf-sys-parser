from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = []

urlpatterns += [
    path('is/api/__docs__/', SpectacularAPIView.as_view(), name='__docs__'),
    path('is/api/', SpectacularSwaggerView.as_view(url_name='__docs__')),
    path('is/api/lessons/', include('app.lessons.urls')),
    path('is/api/employees/', include('app.employees.urls')),
    *static(settings.BASE_STATIC_URL, document_root=settings.STATIC_ROOT),
]
