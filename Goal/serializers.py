from Goal.models import Goal
from rest_framework import serializers


class GoalSerializer(serializers.ModelSerializer):
    """Serialzer for Goal"""
    plans = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    TYPE_CHOICES = [
        ("save_amount", "Save ammount of total income that is more thatn the goal ammount."),
        ("save_percent", "Save percent of the total income based on the goals ammount."),
        ("save_amount_category", "Save ammount of category that is more thatn the goal ammount."),
        ("save_percent_category", "Save percent of the category based on the goals ammount."),
    ]

    type = serializers.ChoiceField(choices=TYPE_CHOICES)

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ['user']
