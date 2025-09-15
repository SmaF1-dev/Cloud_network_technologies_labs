from django.urls import path
from .views import FilmDashboardView

urlpatterns = [
    path('charts/', FilmDashboardView.as_view(), name='film_dashboard'),
    ]
