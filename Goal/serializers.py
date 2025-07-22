from Goal.models import Goal
from rest_framework import serializers


class GoalSerializer(serializers.ModelSerializer):

    plans = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    TYPE_CHOICES = [
        ("savings", "Savings"),
        ("spending_limit", "Spending Limit"),
        ("routine", "Routine"),
        ("custom", "Custom Challenge"),
    ]

    type = serializers.ChoiceField(choices=TYPE_CHOICES)

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ['user']
