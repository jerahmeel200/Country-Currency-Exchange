from django.urls import path
from .views import (
    RefreshCountriesView,
    CountriesListView,
    CountryDetailView,
    StatusView,
    SummaryImageView,
)

urlpatterns = [
    path("refresh", RefreshCountriesView.as_view(), name="countries-refresh"),
    path("", CountriesListView.as_view(), name="countries-list"),
    path("image", SummaryImageView.as_view(), name="countries-image"),
    path("status", StatusView.as_view(), name="countries-status"),
    path("<str:name>", CountryDetailView.as_view(), name="country-detail"),
]
