from rest_framework.routers import DefaultRouter
from SurvivalPlan.views import (
    SurvivalPlanViewSet,
    PlanItemViewSet,
    ExpenseViewSet
)
from django.urls import path, include

router = DefaultRouter()
router.register('survival-plans', SurvivalPlanViewSet, basename='suvivalplan')
router.register('plan-items', PlanItemViewSet, basename='planitem')
router.register('expenses', ExpenseViewSet, basename='expense')

app_name = 'plan'

urlpatterns = [
    path('', include(router.urls)),
]
