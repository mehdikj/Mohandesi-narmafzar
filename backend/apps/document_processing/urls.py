
from django.urls import path

from .views import OCRJobCreateView, OCRJobDetailView


urlpatterns = [
    path(
        "resources/<int:resource_file_id>/ocr/",
        OCRJobCreateView.as_view(),
        name="ocr-job-create",
    ),
    path(
        "ocr/<int:pk>/",
        OCRJobDetailView.as_view(),
        name="ocr-job-detail",
    ),
]
