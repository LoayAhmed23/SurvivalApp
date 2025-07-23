from rest_framework.routers import DefaultRouter
from SurvivalPlan.views import (
    SurvivalPlanViewSet,
    PlanItemViewSet,
    ExpenseViewSet,
    SurvivalPlanGoalsView,
    SurvivalPlanGoalDetailView,
)
from django.urls import path, include

router = DefaultRouter()
router.register('survival-plans', SurvivalPlanViewSet, basename='suvivalplan')
router.register('plan-items', PlanItemViewSet, basename='planitem')
router.register('expenses', ExpenseViewSet, basename='expense')

app_name = 'plan'

urlpatterns = [
    path('', include(router.urls)),
    path('survival-plans/<int:pk>/goals/', SurvivalPlanGoalsView.as_view(), name='survivalplan-goals'),
    path('survival-plans/<int:pk>/goals/<int:goal_pk>/', SurvivalPlanGoalDetailView.as_view(), name='survivalplan-goal-detail'),

]
