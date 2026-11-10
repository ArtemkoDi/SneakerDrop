from django.urls import path

from .views import (
    BrandDetailView,
    BrandListCreateView,
    SneakerDetailView,
    SneakerListCreateView,
    SneakerSizeDetailView,
    SneakerSizeListCreateView,
)

urlpatterns = [
    path("brands/", BrandListCreateView.as_view(), name="brand-list-create"),
    path("brands/<int:pk>/", BrandDetailView.as_view(), name="brand-detail"),
    path("sneakers/", SneakerListCreateView.as_view(), name="sneaker-list-create"),
    path("sneakers/<int:pk>/", SneakerDetailView.as_view(), name="sneaker-detail"),
    path("sizes/", SneakerSizeListCreateView.as_view(), name="size-list-create"),
    path("sizes/<int:pk>/", SneakerSizeDetailView.as_view(), name="size-detail"),
]
