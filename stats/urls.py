from django.urls import path, include
from rest_framework.routers import DefaultRouter
from stats.views import (
    MonthlyStatsView,
    YearlyStatsView,
    MonthlyCategoryStatsView,
    YearlyCategoryStatsView,
)


router = DefaultRouter()


app_name = 'stats'


urlpatterns = [
    path('monthly/', MonthlyStatsView.as_view()),
    path('monthly/<str:month>/', MonthlyStatsView.as_view()),
    path('yearly/', YearlyStatsView.as_view()),
    path('yearly/<int:year>/', YearlyStatsView.as_view()),
    path('category/<str:category>/monthly/', MonthlyCategoryStatsView.as_view()),
    path('category/<str:category>/monthly/<str:month>/', MonthlyCategoryStatsView.as_view()),
    path('category/<str:category>/yearly/', YearlyCategoryStatsView.as_view()),
    path('category/<str:category>/yearly/<int:year>/', YearlyCategoryStatsView.as_view()),
]
