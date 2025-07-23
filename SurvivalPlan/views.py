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
from Goal.serializers import GoalSerializer
from Goal.models import Goal

from datetime import date

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response


def get_monthly_expenses(user, month):
    """Helper function to calculate expenses for a given month"""
    month_expenses = Expense.objects.filter(
        user=user,
        date__year=month.year,
        date__month=month.month
    )
    return sum(exp.amount for exp in month_expenses)


def get_monthly_category_expenses(user, month, category):
    """Helper function to calculate expenses for a given month with a certain category"""

    month_expenses = Expense.objects.filter(
        user=user,
        date__year=month.year,
        date__month=month.month,
        category=category
    )
    return sum(exp.amount for exp in month_expenses)


def check_goal_status(goal, plan, user):
    """Helper function to check if goal is achieved or not"""

    today = date.today()
    if plan.month.year > today.year or (plan.month.year == today.year and plan.month.month >= today.month):
        """If month has not ended yet cannot determine goal result"""
        return 'Plan\'s month has not ended yet'

    if goal.type == 'save_amount':
        total_expenses = get_monthly_expenses(user, plan.month)
        if (plan.income - total_expenses) >= goal.target_amount:
            return "Goal Achieved"
        else:
            return "Goal Not Achieved"

    elif goal.type == 'save_percent':
        total_expenses = get_monthly_expenses(user, plan.month)
        required_saved = (goal.target_amount / 100) * plan.income
        actual_saved = plan.income - total_expenses
        if actual_saved >= required_saved:
            return "Goal Achieved"
        else:
            return "Goal Not Achieved"

    elif goal.type == 'save_amount_category':
        try:
            planitem = PlanItem.objects.get(plan=plan, category=goal.category)
        except PlanItem.DoesNotExist:
            return "No plan item with the given category, cannot achieve goal"

        total_category_expenses = get_monthly_category_expenses(user, plan.month, goal.category)
        if (planitem.amount - total_category_expenses) >= goal.target_amount:
            return "Goal Achieved"
        else:
            return "Goal Not Achieved"

    elif goal.type == 'save_percent_category':
        try:
            planitem = PlanItem.objects.get(plan=plan, category=goal.category)
        except PlanItem.DoesNotExist:
            return "No plan item with the given category, cannot achieve goal"

        total_category_expenses = get_monthly_category_expenses(user, plan.month, goal.category)

        required_saved = (goal.target_amount / 100) * planitem.amount
        actual_saved = planitem.amount - total_category_expenses
        if actual_saved >= required_saved:
            return "Goal Achieved"
        else:
            return "Goal Not Achieved"

    return "Goal Type Not Valid"


class SurvivalPlanViewSet(viewsets.ModelViewSet):
    """View for Survival Plan CRUD operations"""

    serializer_class = SurvivalPlanSerializer

    def get_queryset(self):
        return SurvivalPlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PlanItemViewSet(viewsets.ModelViewSet):
    """View for PlanItem CRUD operations"""
    serializer_class = PlanItemSerializer

    def get_queryset(self):
        return PlanItem.objects.filter(plan__user=self.request.user)


class ExpenseViewSet(viewsets.ModelViewSet):
    """View for ViewSet CRUD operations"""
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SurvivalPlanGoalsView(APIView):
    """View to list goals for a survival plan and if they are completed or not"""

    def get(self, request, pk):
        try:
            plan = SurvivalPlan.objects.get(pk=pk, user=request.user)
        except SurvivalPlan.DoesNotExist:
            return Response({'detail': 'Plan not found.'}, status=status.HTTP_404_NOT_FOUND)

        goals = plan.goals.all()
        data = []

        for goal in goals:
            serializer = GoalSerializer(goal)
            achieved = check_goal_status(goal, plan, request.user)
            data.append({
                **serializer.data,
                'achieved': achieved
            })

        return Response(data)


class SurvivalPlanGoalDetailView(APIView):
    """View to see if a specific goal for a survival plan is completed or not"""

    def get(self, request, pk, goal_pk):
        try:
            plan = SurvivalPlan.objects.get(pk=pk, user=request.user)
        except SurvivalPlan.DoesNotExist:
            return Response({'detail': 'Plan not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            goal = plan.goals.get(pk=goal_pk)
        except Goal.DoesNotExist:
            return Response({'detail': 'Goal not found in this plan.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = GoalSerializer(goal)
        achieved = check_goal_status(goal, plan, request.user)
        return Response({
            **serializer.data,
            'achieved': achieved
        })
