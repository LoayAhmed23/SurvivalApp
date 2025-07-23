from Goal.models import Goal
from rest_framework import serializers


class GoalSerializer(serializers.ModelSerializer):
    """Serialzer for Goal"""
    plans = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    TYPE_CHOICES = [
        ("save_amount", "Save amount of total income that is more thatn the goal amount."),
        ("save_percent", "Save percent of the total income based on the goals amount."),
        ("save_amount_category", "Save amount of category that is more thatn the goal amount."),
        ("save_percent_category", "Save percent of the category based on the goals amount."),
    ]

    type = serializers.ChoiceField(choices=TYPE_CHOICES)

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ['user']
