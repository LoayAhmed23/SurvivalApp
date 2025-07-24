from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date, timedelta

from SurvivalPlan.models import (
    SurvivalPlan,
    Expense,
    PlanItem,
)

class MonthlyStatsView(APIView):

    def get(self, request, month=None):
        user = request.user
        today = date.today()

        if month is not None:
            try:
                year, month_num = map(int, month.split('-'))
            except (ValueError, TypeError):
                return Response("Invalid month format. Use YYYY-MM.", status=status.HTTP_400_BAD_REQUEST)
        else:
            year, month_num = today.year, today.month

        try:
            plan = SurvivalPlan.objects.get(user=user, month__year=year, month__month=month_num)
            income = plan.income
        except SurvivalPlan.DoesNotExist:
            return Response("No plan at the given month", status=status.HTTP_404_NOT_FOUND)


        expenses = Expense.objects.filter(user=user, date__year=year, date__month=month_num)
        total_expenses = sum(exp.amount for exp in expenses)

        return Response({
            "month": f"{year}-{month_num:02}",
            "income": income,
            "total_expense": total_expenses,
            "net_savings": income - total_expenses,
        })


class YearlyStatsView(APIView):

    def get(self, request, year=None):
        user = request.user
        today = date.today()

        if year is not None:
            start = date(year, 1, 1)
            end = date(year, 12, 1)
        else:
            start = today - timedelta(days=365)
            end = today

        plans = SurvivalPlan.objects.filter(user=user, month__range=(start, end))
        expenses = Expense.objects.filter(user=user, date__range=(start, end))

        monthly_data = {}
        months = []
        start_year = start.year
        start_month = start.month

        for i in range(12):
            month = (start_month + i - 1) % 12 + 1
            year = start_year + (start_month + i - 1) // 12
            months.append(date(year, month, 1))
        
        for month in months:
            try:
                plan = plans.get(month__year=month.year, month__month=month.month)
                income = plan.income
            except SurvivalPlan.DoesNotExist:
                continue
            monthly_expenses = expenses.filter(date__year=month.year, date__month=month.month)
            total_expense = sum(exp.amount for exp in monthly_expenses)

            monthly_data[month.strftime('%Y-%m')] = {
                "income": income,
                "total_expense": total_expense,
                "net_savings": income - total_expense
            }

        total_income = sum(m["income"] for m in monthly_data.values())
        total_expense = sum(exp.amount for exp in expenses)
        plan_expense = sum(m["total_expense"] for m in monthly_data.values())

        return Response({
            "range": f"{months[0].strftime('%Y-%m')} to {months[11].strftime('%Y-%m')}",
            "total_income": total_income,
            "total_expense": total_expense,
            "net_savings": total_income - total_expense,
            "epenses_not_convered_by_any_plan": total_expense - plan_expense,
            "number_of_plans": len(monthly_data),
            "monthly_breakdown": monthly_data
        })


class MonthlyCategoryStatsView(APIView):

    def get(self, request, category=None,  month=None):
        user = request.user
        today = date.today()

        if category is None:
            return Response("Category is not entered.", status=status.HTTP_400_BAD_REQUEST)

        if month is not None:
            try:
                year, month_num = map(int, month.split('-'))
            except (ValueError, TypeError):
                return Response(
                    "Invalid month format. Use YYYY-MM.",
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            year, month_num = today.year, today.month

        try:
            plan = SurvivalPlan.objects.get(
                user=user,
                month__year=year,
                month__month=month_num
            )
            planitem = PlanItem.objects.get(plan=plan, category=category)
            amount = planitem.amount
        except SurvivalPlan.DoesNotExist or PlanItem.DoesNotExist:
            return Response(
                "No plan at the given month has this cateogry",
                status=status.HTTP_404_NOT_FOUND
            )


        expenses = Expense.objects.filter(
            user=user,
            date__year=year,
            date__month=month_num,
            category=category
        )

        total_expenses = sum(exp.amount for exp in expenses)

        return Response({
            "month": f"{year}-{month_num:02}",
            "category": category,
            "amount": amount,
            "total_expense": total_expenses,
            "net_savings": amount - total_expenses,
        })


class YearlyCategoryStatsView(APIView):

    def get(self, request, category=None, year=None):
        user = request.user
        today = date.today()

        if year is not None:
            start = date(year, 1, 1)
            end = date(year, 12, 1)
        else:
            start = today - timedelta(days=365)
            end = today

        plans = SurvivalPlan.objects.filter(user=user, month__range=(start, end))
        expenses = Expense.objects.filter(
            user=user,
            category=category,
            date__range=(start, end)
        )

        monthly_data = {}
        months = []
        start_year = start.year
        start_month = start.month

        for i in range(12):
            month = (start_month + i - 1) % 12 + 1
            year = start_year + (start_month + i - 1) // 12
            months.append(date(year, month, 1))
        
        for month in months:
            try:
                plan = plans.get(month__year=month.year, month__month=month.month)
                planitem = PlanItem.objects.get(plan=plan, category=category)
                amount = planitem.amount
            except SurvivalPlan.DoesNotExist or PlanItem.DoesNotExist:
                continue

            monthly_expenses = expenses.filter(date__year=month.year, date__month=month.month)
            total_expense = sum(exp.amount for exp in monthly_expenses)

            monthly_data[month.strftime('%Y-%m')] = {
                "amount": amount,
                "total_expense": total_expense,
                "net_savings": amount - total_expense
            }

        total_amount = sum(m["amount"] for m in monthly_data.values())
        total_expense = sum(exp.amount for exp in expenses)
        plan_expense = sum(m["total_expense"] for m in monthly_data.values())

        return Response({
            "range": f"{months[0].strftime('%Y-%m')} to {months[11].strftime('%Y-%m')}",
            "category": category,
            "total_amount": total_amount,
            "total_expense": total_expense,
            "net_savings": total_amount - total_expense,
            "epenses_not_convered_by_any_plan": total_expense - plan_expense,
            "number_of_plans": len(monthly_data),
            "monthly_breakdown": monthly_data
        })