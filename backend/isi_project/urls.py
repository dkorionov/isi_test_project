from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings

admin.site.index_title = "ISI-Project Admin Panel"
admin.site.site_header = "ISI-Project Admin Panel"
admin.site.site_title = "ISI-Project Admin Panel"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('rest_framework.urls')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path(
        "api/v1/", include(
            [
                path(
                    "oauth/", include([
                        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
                        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
                    ]),
                ),
                path("threads/", include("threads.urls")),
            ],
        ),
    ),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += list(
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    )
