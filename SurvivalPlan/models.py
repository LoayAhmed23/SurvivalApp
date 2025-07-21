from django.db import models
from django.contrib.auth import get_user_model
from datetime import date
User = get_user_model()


class SurvivalPlan(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    income = models.PositiveIntegerField()
    month = models.DateField()

    def __str__(self):
        """Overriding the str opperator"""
        return self.title


class PlanItem(models.Model):
    plan = models.ForeignKey(
        SurvivalPlan,
        on_delete=models.CASCADE,
        related_name='items'
    )
    category = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    amount = models.PositiveIntegerField()

    def __str__(self):
        """Overriding the str opperator"""
        return self.category


class Expense(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    amount = models.PositiveIntegerField(default=0)
    date = models.DateField(default=date.today)

    def __str__(self):
        """Overriding the str opperator"""
        return self.title
