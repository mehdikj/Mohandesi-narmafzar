from django.urls import path

from .views import (
    AuthorListCreateView,
    CategoryListCreateView,
    ResourceListCreateView,
    ResourceDetailView,
    ResourceFileDownloadView,
)

urlpatterns = [
    path("authors/", AuthorListCreateView.as_view(), name="author-list"),
    path("categories/", CategoryListCreateView.as_view(), name="category-list"),
    path("resources/", ResourceListCreateView.as_view(), name="resource-list"),
    path("resources/<int:pk>/", ResourceDetailView.as_view(), name="resource-detail"),
    path(
        "resources/<int:resource_id>/files/<int:file_id>/download/",
        ResourceFileDownloadView.as_view(),
        name="resource-file-download",
    ),
]