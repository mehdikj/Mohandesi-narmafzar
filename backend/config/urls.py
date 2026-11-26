from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.identity.urls")),
    path("api/v1/", include("apps.resources.urls")),
    path("api/v1/", include("apps.document_processing.urls")),
    path("api/v1/", include("apps.favorites.urls")),
    path("api/v1/", include("apps.subscriptions.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
