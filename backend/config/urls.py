from django.conf import settings
from django.urls import URLPattern, URLResolver, include, path

urlpatterns: list[URLPattern | URLResolver] = [
    path("api/auth/", include("apps.account.urls")),
    path("api/vsosh/", include("apps.vsosh.urls")),
]

# В режиме разработки
if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static
    from drf_yasg import openapi, views
    from rest_framework import permissions

    # Основной Swagger
    schema_view = views.get_schema_view(
        openapi.Info(title="API", default_version="v1"),
        public=True,
        permission_classes=[permissions.AllowAny],
    )

    # Swagger только для Auth
    auth_patterns: list[URLPattern | URLResolver] = [
        path("api/auth/", include("apps.account.urls"))
    ]
    schema_auth = views.get_schema_view(
        openapi.Info(title="Auth API", default_version="v1"),
        public=True,
        permission_classes=[permissions.AllowAny],
        patterns=auth_patterns,
    )

    # Swagger только для VSOSH
    vsosh_patterns: list[URLPattern | URLResolver] = [
        path("api/vsosh/", include("apps.vsosh.urls"))
    ]
    schema_vsosh = views.get_schema_view(
        openapi.Info(title="VSOSH API", default_version="v1"),
        public=True,
        permission_classes=[permissions.AllowAny],
        patterns=vsosh_patterns,
    )

    urlpatterns += [
        path("", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-all"),
        path("swagger/auth/", schema_auth.with_ui("swagger", cache_timeout=0), name="swagger-auth"),
        path(
            "swagger/vsosh/", schema_vsosh.with_ui("swagger", cache_timeout=0), name="swagger-vsosh"
        ),
    ]

    # Django Debug Toolbar
    toolbar_urls: list[URLPattern | URLResolver] = [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
    urlpatterns = toolbar_urls + urlpatterns

    # Статика и медиа (их нет)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
