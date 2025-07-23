from SurvivalPlan.models import (
    PlanItem,
    SurvivalPlan,
    Expense
)
from Goal.models import Goal

from rest_framework import serializers
from datetime import date


class PlanItemSerializer(serializers.ModelSerializer):
    """Serialzer for planitems"""
    class Meta:
        model = PlanItem
        fields = '__all__'

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user

        if self.instance:
            plan = attrs.get('plan') or (self.instance.plan)
            new_amount = attrs.get('amount', self.instance.amount)

            if new_amount == self.instance.amount and plan == self.instance.plan:
                return attrs

            if plan != self.instance.plan:
                if user != plan.user:
                    raise serializers.ValidationError("You do not own the selected plan.")

                related_items = PlanItem.objects.filter(plan=plan)
                total_with_new = new_amount + sum(item.amount for item in related_items)

                if total_with_new > plan.income:
                    raise serializers.ValidationError(
                        "Moving this item will exceed the new plan's income "
                        f"by ({total_with_new - plan.income})"
                    )
            else:
                related_items = PlanItem.objects.filter(plan=plan).exclude(pk=self.instance.pk)
                total_with_new = new_amount + sum(item.amount for item in related_items)
                if total_with_new > plan.income:
                    raise serializers.ValidationError(
                        "Editing this item will exceed the income "
                        f"by ({total_with_new - plan.income})"
                    )

        else:

            plan = attrs.get('plan')
            new_amount = attrs.get('amount', 0)

            if user != plan.user:
                raise serializers.ValidationError("You do not own the selected plan.")

            related_items = PlanItem.objects.filter(plan=plan)
            total_with_new = new_amount + sum(item.amount for item in related_items)
            if total_with_new > plan.income:
                raise serializers.ValidationError(
                    f"Adding this item will exceed the income by ({total_with_new - plan.income})"
                )

        return attrs


class SurvivalPlanSerializer(serializers.ModelSerializer):
    """Serialzer for survivalplans"""
    items = PlanItemSerializer(many=True, read_only=True)

    class Meta:
        model = SurvivalPlan
        fields = '__all__'
        read_only_fields = ['user']

    goals = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Goal.objects.all(),
        required=False
    )

    def create(self, validated_data):
        goals = validated_data.pop('goals', [])
        plan = super().create(validated_data)
        plan.goals.set(goals)
        return plan

    def update(self, instance, validated_data):
        goals = validated_data.pop('goals', None)
        plan = super().update(instance, validated_data)
        if goals is not None:
            plan.goals.set(goals)
        return plan

    def validate_month(self, value):
        return date(value.year, value.month, 1)

    def to_internal_value(self, data):
        """Accept only date as YYYY-MM"""
        month_str = data.get('month')
        if isinstance(month_str, str):
            try:
                year, month = map(int, month_str.split('-'))
                data['month'] = date(year, month, 1)
            except (ValueError, TypeError):
                raise serializers.ValidationError({
                    "month": "Invalid format. Use YYYY-MM."
                })
        return super().to_internal_value(data)

    def to_representation(self, instance):
        """Display plan's month as YYYY-MM"""

        data = super().to_representation(instance)

        if 'month' in data and instance.month:
            data['month'] = instance.month.strftime('%Y-%m')
        return data


class ExpenseSerializer(serializers.ModelSerializer):
    """Serialzer for expenses"""
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ['user']
