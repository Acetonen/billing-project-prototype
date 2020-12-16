from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

api_urlpatterns = [
    path("accounts/", include("project.accounts.urls")),
    path("payments/", include("project.payments.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_urlpatterns)),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

schema_view = get_schema_view(
    openapi.Info(
        title="Billing API",
        default_version="v1",
    ),
    public=False,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns += [
    path(
        "billing/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "billing/swagger<str:format>",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "billing/redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
]
