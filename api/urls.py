from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = []

urlpatterns += [
    path('inf-sys-parser/api/__docs__/', SpectacularAPIView.as_view(), name='__docs__'),
    path('inf-sys-parser/api/', SpectacularSwaggerView.as_view(url_name='__docs__')),
    path('inf-sys-parser/api/lessons/', include('app.lessons.urls')),
    path('inf-sys-parser/api/employees/', include('app.employees.urls')),
    *static(settings.BASE_STATIC_URL, document_root=settings.STATIC_ROOT),
]
