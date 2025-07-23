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
from rest_framework.pagination import PageNumberPagination

from django.db import connection, reset_queries  # SQL DEBUG


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


def check_goal_status(goal, plan, user, expenses):
    """Helper function to check if goal is achieved or not"""

    today = date.today()
    if plan.month.year > today.year or (plan.month.year == today.year and plan.month.month >= today.month):
        """If month has not ended yet cannot determine goal result"""
        return "Plan's month has not ended yet"

    if goal.type == 'save_amount':
        if (plan.income - expenses) >= goal.target_amount:
            return "Goal Achieved"
        else:
            return "Goal Not Achieved"

    elif goal.type == 'save_percent':
        required_saved = (goal.target_amount / 100) * plan.income
        actual_saved = plan.income - expenses

        if actual_saved >= required_saved:
            return "Goal Achieved"
        else:
            return "Goal Not Achieved"

    elif goal.type == 'save_amount_category':
        try:
            planitem = PlanItem.objects.get(plan=plan, category=goal.category)
        except PlanItem.DoesNotExist:
            return "No plan item with the given category, cannot achieve goal"

        if (planitem.amount - expenses) >= goal.target_amount:
            return "Goal Achieved"
        else:
            return "Goal Not Achieved"

    elif goal.type == 'save_percent_category':
        try:
            planitem = PlanItem.objects.get(plan=plan, category=goal.category)
        except PlanItem.DoesNotExist:
            return "No plan item with the given category, cannot achieve goal"

        required_saved = (goal.target_amount / 100) * planitem.amount
        actual_saved = planitem.amount - expenses

        if actual_saved >= required_saved:
            return "Goal Achieved"
        else:
            return "Goal Not Achieved"

    return "Goal Type Not Valid"


class SurvivalPlanViewSet(viewsets.ModelViewSet):
    """View for Survival Plan CRUD operations"""

    serializer_class = SurvivalPlanSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return SurvivalPlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PlanItemViewSet(viewsets.ModelViewSet):
    """View for PlanItem CRUD operations"""
    serializer_class = PlanItemSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return PlanItem.objects.filter(plan__user=self.request.user)


class ExpenseViewSet(viewsets.ModelViewSet):
    """View for ViewSet CRUD operations"""
    serializer_class = ExpenseSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SurvivalPlanGoalsView(APIView):
    """View to list goals for a survival plan and if they are completed or not"""

    def get(self, request, pk):
        reset_queries()  # SQL DEBUG

        try:
            plan = SurvivalPlan.objects.get(pk=pk, user=request.user)
        except SurvivalPlan.DoesNotExist:
            return Response({'detail': 'Plan not found.'}, status=status.HTTP_404_NOT_FOUND)
        goals = plan.goals.all()
        data = []
        month_expenses = Expense.objects.filter(
            user=request.user,
            date__year=plan.month.year,
            date__month=plan.month.month
        )
        total_expenses = sum(exp.amount for exp in month_expenses)

        category_expense_cache = {}

        for goal in goals:
            serializer = GoalSerializer(goal)

            if goal.type == 'save_amount' or goal.type == 'save_percent':
                expenses = total_expenses

            else:
                if goal.category in category_expense_cache:
                    expenses = category_expense_cache[goal.category]
                else:
                    category_expenses = month_expenses.filter(category=goal.category)
                    expenses = sum(exp.amount for exp in category_expenses)
                    category_expense_cache[goal.category] = expenses

            achieved = check_goal_status(goal, plan, request.user, expenses)

            data.append({
                **serializer.data,
                'achieved': achieved
            })

        for q in connection.queries:  # SQL DEBUG
            print(q['sql'], "\n", q['time'], "\n")  # SQL DEBUG

        return Response(data)


class SurvivalPlanGoalDetailView(APIView):
    """View to see if a specific goal for a survival plan is completed or not"""

    def get(self, request, pk, goal_pk):
        try:
            plan = SurvivalPlan.objects.get(pk=pk, user=request.user)
        except SurvivalPlan.DoesNotExist:
            return Response({'detail': 'Plan not found.'},
                            status=status.HTTP_404_NOT_FOUND)

        try:
            goal = plan.goals.get(pk=goal_pk)
        except Goal.DoesNotExist:
            return Response({'detail': 'Goal not found in this plan.'},
                            status=status.HTTP_404_NOT_FOUND)

        if goal.type == 'save_amount' or goal.type == 'save_percent':
            month_expenses = Expense.objects.filter(
                user=request.user,
                date__year=plan.month.year,
                date__month=plan.month.month
            )
            total_expenses = sum(exp.amount for exp in month_expenses)
        else:
            month_expenses = Expense.objects.filter(
                user=request.user,
                date__year=plan.month.year,
                date__month=plan.month.month,
                category=goal.category
            )
            total_expenses = sum(exp.amount for exp in month_expenses)

        achieved = check_goal_status(goal, plan, request.user, total_expenses)

        serializer = GoalSerializer(goal)

        return Response({
            **serializer.data,
            'achieved': achieved
        })
