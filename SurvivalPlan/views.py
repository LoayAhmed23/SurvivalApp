from SurvivalPlan.serializers import (
    PlanItemSerializer,
    SurvivalPlanSerializer,
    ExpenseSerializer,
)
from SurvivalPlan.models import (
    Expense,
    PlanItem,
    SurvivalPlan,
)

from rest_framework import viewsets

# def get_monthly_expenses(self, user, month):
#     """Helper function to calculate expenses for a given month"""
#     month_expenses = Expense.objects.filter(
#         user=user,
#         date__year=month.year,
#         date__month=month.month
#     )
#     return sum(exp.amount for exp in month_expenses)


class SurvivalPlanViewSet(viewsets.ModelViewSet):
    serializer_class = SurvivalPlanSerializer
    
    def get_queryset(self):
        return SurvivalPlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PlanItemViewSet(viewsets.ModelViewSet):
    serializer_class = PlanItemSerializer

    def get_queryset(self):
        return PlanItem.objects.filter(plan__user=self.request.user)


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)
    
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
