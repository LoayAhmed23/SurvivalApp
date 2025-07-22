from django.urls import path, include
from rest_framework.routers import DefaultRouter

from Goal.views import GoalViewSet


router = DefaultRouter()
router.register('goals', GoalViewSet, basename='goals')


app_name = 'goal'


urlpatterns = [
    path('', include(router.urls)),
]
